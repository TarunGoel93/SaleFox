"""
JioMart Pro Intelligence Web Server
Flask Backend Server providing real-time scraping controls and streaming data
"""

import os
import io
import re
import json
import threading
import logging
from datetime import datetime
from typing import Dict, Any, List

from flask import Flask, request, jsonify, send_file, send_from_directory, Response
from flask_cors import CORS
import pandas as pd

from jiomart_scraper import JioMartScraper

# Initialize Flask application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
SCRAPED_DIR = os.path.join(BASE_DIR, "scraped_data")
os.makedirs(SCRAPED_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

app = Flask(__name__, static_folder=WEB_DIR, static_url_path="")
CORS(app)

# Global thread-safe scraper state
state_lock = threading.Lock()
current_job_id = 0
job_state: Dict[str, Any] = {
    "job_id": 0,
    "status": "idle",       # "idle", "running", "completed", "error"
    "progress": 0,          # 0 to 100
    "current_query": "",
    "pincode": "110058",
    "logs": [],             # List of {"time": str, "msg": str, "pct": int}
    "products": [],         # List of normalized products
    "error_message": "",
    "updated_at": datetime.now().isoformat()
}

# Pre-load existing data if available
json_cache = os.path.join(SCRAPED_DIR, "jiomart_products.json")
if os.path.exists(json_cache):
    try:
        with open(json_cache, "r", encoding="utf-8") as f:
            cached = json.load(f)
            if isinstance(cached, list) and cached:
                job_state["products"] = cached
                job_state["status"] = "completed"
                job_state["progress"] = 100
                job_state["logs"].append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "msg": f"Loaded {len(cached)} existing product listings from disk.",
                    "pct": 100
                })
    except Exception as e:
        logging.warning(f"Could not load pre-cached products: {e}")


def progress_tracker(message: str, pct: int = -1):
    """Callback invoked by JioMartScraper to stream real-time logs."""
    with state_lock:
        if pct >= 0:
            job_state["progress"] = pct
        timestamp = datetime.now().strftime("%H:%M:%S")
        job_state["logs"].append({
            "time": timestamp,
            "msg": message,
            "pct": job_state["progress"]
        })
        # Keep latest 100 log lines
        if len(job_state["logs"]) > 100:
            job_state["logs"] = job_state["logs"][-100:]
        job_state["updated_at"] = datetime.now().isoformat()


def run_scraping_worker(job_id: int, query: str, pages: int, pincode: str, in_stock_only: bool, min_price: Any, max_price: Any):
    """Worker executed in background daemon thread."""
    try:
        def step_cb(msg: str, pct: int):
            with state_lock:
                if job_state.get("job_id") != job_id:
                    return
            progress_tracker(msg, pct)

        scraper = JioMartScraper(pincode=pincode, progress_cb=step_cb)
        results = scraper.scrape_catalog(
            query=query,
            pages=pages,
            in_stock_only=in_stock_only,
            min_price=min_price,
            max_price=max_price
        )
        with state_lock:
            if job_state.get("job_id") != job_id:
                return
            job_state["status"] = "completed"
            job_state["progress"] = 100
            job_state["products"] = results
            job_state["updated_at"] = datetime.now().isoformat()
            job_state["logs"].append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "msg": f"Scrape completed successfully: {len(results)} handsets found.",
                "pct": 100
            })
    except Exception as exc:
        logging.error(f"Scraping task failure: {exc}", exc_info=True)
        with state_lock:
            if job_state.get("job_id") != job_id:
                return
            job_state["status"] = "error"
            job_state["progress"] = 100
            job_state["error_message"] = str(exc)
            job_state["updated_at"] = datetime.now().isoformat()
            job_state["logs"].append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "msg": f"ERROR: {str(exc)}",
                "pct": 100
            })


@app.route("/")
def index():
    """Serve frontend single page application if index.html exists."""
    index_file = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_file):
        return send_from_directory(WEB_DIR, "index.html")
    return jsonify({
        "service": "JioMart Pro Intelligence Scraper API",
        "port": 5062,
        "status": "online",
        "endpoints": ["/api/status", "/api/scrape", "/api/export-csv", "/api/export-json"]
    })


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/<path:path>")
def static_proxy(path):
    """Serve frontend static assets."""
    if os.path.exists(os.path.join(WEB_DIR, path)):
        return send_from_directory(WEB_DIR, path)
    return jsonify({"error": "Not found"}), 404


@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    """Trigger a new scraping task."""
    global current_job_id
    data = request.get_json(force=True, silent=True) or {}
    query = str(data.get("query") or "").strip()
    if not query:
        return jsonify({"success": False, "error": "Query parameter cannot be empty."}), 400

    pages = int(data.get("pages") or 2)
    pages = max(1, min(pages, 4))
    pincode = str(data.get("pincode") or "110058").strip()
    in_stock_only = bool(data.get("in_stock_only", False))
    min_price = float(data["min_price"]) if data.get("min_price") is not None and data["min_price"] != "" else None
    max_price = float(data["max_price"]) if data.get("max_price") is not None and data["max_price"] != "" else None

    with state_lock:
        if job_state["status"] == "running" and job_state.get("current_query", "").lower() == query.lower():
            return jsonify({
                "success": True,
                "message": "Scraping already running for this query",
                "query": query,
                "job_id": job_state.get("job_id", 0)
            })

        current_job_id += 1
        active_id = current_job_id
        job_state["job_id"] = active_id
        job_state["status"] = "running"
        job_state["progress"] = 5
        job_state["current_query"] = query
        job_state["pincode"] = pincode
        job_state["products"] = []  # Clear previous products
        job_state["error_message"] = ""
        job_state["updated_at"] = datetime.now().isoformat()
        job_state["logs"] = [{
            "time": datetime.now().strftime("%H:%M:%S"),
            "msg": f"Dispatched JioMart scrape request for '{query}' (pages={pages}, pincode={pincode})",
            "pct": 5
        }]

    worker = threading.Thread(
        target=run_scraping_worker,
        args=(active_id, query, pages, pincode, in_stock_only, min_price, max_price),
        daemon=True
    )
    worker.start()

    return jsonify({
        "success": True,
        "message": "Scraping job started",
        "query": query,
        "job_id": active_id,
        "pincode": pincode,
        "pages": pages
    })


@app.route("/api/status", methods=["GET"])
def api_status():
    """Returns current job status, streaming logs, and product data."""
    with state_lock:
        response_data = {
            "job_id": job_state.get("job_id", 0),
            "status": job_state["status"],
            "progress": job_state["progress"],
            "query": job_state["current_query"],
            "pincode": job_state["pincode"],
            "logs": list(job_state["logs"]),
            "products": list(job_state["products"]),
            "count": len(job_state["products"]),
            "error": job_state["error_message"],
            "updated_at": job_state["updated_at"]
        }
    return jsonify(response_data)


@app.route("/api/export-csv", methods=["GET"])
def api_export_csv():
    """Stream clean CSV file of current scraped products."""
    with state_lock:
        products = list(job_state["products"])

    if not products:
        csv_disk = os.path.join(SCRAPED_DIR, "jiomart_products.csv")
        if os.path.exists(csv_disk):
            return send_file(
                csv_disk,
                mimetype="text/csv",
                as_attachment=True,
                download_name="jiomart_products.csv"
            )
        return jsonify({"error": "No data available to export"}), 404

    csv_rows = []
    for p in products:
        r = dict(p)
        if isinstance(r.get("specs"), list):
            r["specs"] = ", ".join(r["specs"])
        csv_rows.append(r)

    df = pd.DataFrame(csv_rows)
    buf = io.BytesIO()
    df.to_csv(buf, index=False, encoding="utf-8")
    buf.seek(0)

    filename = f"jiomart_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@app.route("/api/export-json", methods=["GET"])
def api_export_json():
    """Stream clean JSON file of current scraped products."""
    with state_lock:
        products = list(job_state["products"])

    if not products:
        json_disk = os.path.join(SCRAPED_DIR, "jiomart_products.json")
        if os.path.exists(json_disk):
            return send_file(
                json_disk,
                mimetype="application/json",
                as_attachment=True,
                download_name="jiomart_products.json"
            )
        return jsonify({"error": "No data available to export"}), 404

    buf = io.BytesIO()
    buf.write(json.dumps(products, indent=2, ensure_ascii=False).encode("utf-8"))
    buf.seek(0)

    filename = f"jiomart_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return Response(
        buf.getvalue(),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "JioMart Scraper",
        "port": 5062,
        "timestamp": datetime.now().isoformat()
    })


# ---------------- JioMart Automation API Integration ----------------
import sys
backend_dir = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from unified_automation import attach_flask_automation_routes

attach_flask_automation_routes(app, 'jiomart')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5062))
    print(f"=====================================================")
    print(f"  JioMart Pro Intelligence Web Server Running")
    print(f"  Local API: http://localhost:{port}")
    print(f"  Status Endpoint: http://localhost:{port}/api/status")
    print(f"  Scrape Endpoint: http://localhost:{port}/api/scrape")
    print(f"=====================================================")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

