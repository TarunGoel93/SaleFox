"""
Oppo Intelligence Pro - Web API & Automated Purchasing Server
Flask Backend Server providing real-time scraping controls and streaming data
Port: 5057
"""

import os
import sys
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

from oppo_scraper import OppoScraperEngine

# Initialize Flask application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
SCRAPED_DIR = os.path.join(BASE_DIR, "scraped_data")
os.makedirs(SCRAPED_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

app = Flask(__name__, static_folder=WEB_DIR, static_url_path="")
CORS(app)

scraper_engine = OppoScraperEngine(data_dir=SCRAPED_DIR)

# Global thread-safe scraper state
state_lock = threading.RLock()
current_job_id = 0
job_state: Dict[str, Any] = {
    "job_id": 0,
    "status": "idle",       # "idle", "running", "completed", "error"
    "progress": 0,          # 0 to 100
    "current_query": "",
    "pincode": "700092",
    "logs": [],             # List of {"time": str, "msg": str, "pct": int}
    "products": [],         # List of normalized products
    "error_message": "",
    "updated_at": datetime.now().isoformat()
}

# Pre-load existing data if available or generate from master catalog
json_cache = os.path.join(SCRAPED_DIR, "oppo_products.json")
cached_items = []
if os.path.exists(json_cache):
    try:
        with open(json_cache, "r", encoding="utf-8") as f:
            cached_items = json.load(f)
    except Exception as e:
        logging.warning(f"Could not load pre-cached Oppo products: {e}")

if not cached_items or len(cached_items) == 0:
    cached_items = scraper_engine.scrape("All", pincode="700092")

job_state["products"] = cached_items
job_state["status"] = "completed"
job_state["progress"] = 100
job_state["logs"].append({
    "time": datetime.now().strftime("%H:%M:%S"),
    "msg": f"Loaded {len(cached_items)} authentic Oppo smartphone variants.",
    "pct": 100
})


def progress_tracker(message: str, pct: int = -1):
    """Callback invoked by OppoScraperEngine to stream real-time logs."""
    with state_lock:
        if pct >= 0:
            job_state["progress"] = pct
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {
            "time": timestamp,
            "msg": message,
            "pct": job_state["progress"]
        }
        job_state["logs"].append(entry)
        if len(job_state["logs"]) > 100:
            job_state["logs"].pop(0)
        job_state["updated_at"] = datetime.now().isoformat()
        print(f"[{timestamp}] [OPPO] {message}")


def run_scraping_worker(job_id: int, query: str, pincode: str, in_stock_only: bool):
    """Background worker for Oppo scraping."""
    global job_state
    try:
        with state_lock:
            job_state["status"] = "running"
            job_state["progress"] = 5
            job_state["current_query"] = query
            job_state["pincode"] = pincode
            job_state["logs"] = []
            job_state["error_message"] = ""

        progress_tracker(f"Initiating Oppo Intelligence Scraper for '{query}' [PIN: {pincode}]", 10)

        results = scraper_engine.scrape(
            query=query,
            pincode=pincode,
            in_stock_only=in_stock_only,
            log_callback=lambda m: progress_tracker(m)
        )

        with state_lock:
            job_state["products"] = results
            job_state["status"] = "completed"
            job_state["progress"] = 100
        progress_tracker(f"Scrape completed successfully. {len(results)} authentic Oppo devices available.", 100)

    except Exception as e:
        logging.exception("Error during Oppo scrape execution")
        with state_lock:
            job_state["status"] = "error"
            job_state["error_message"] = str(e)
            job_state["progress"] = 100
        progress_tracker(f"Fatal error: {str(e)}", 100)


@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    """Trigger background scraping job for Oppo."""
    global current_job_id
    data = request.get_json(silent=True) or {}
    query = data.get("query", "All").strip()
    pincode = data.get("pincode", "700092").strip()
    in_stock_only = bool(data.get("in_stock_only", False))

    with state_lock:
        if job_state["status"] == "running":
            return jsonify({
                "success": False,
                "message": "A scraping job is already running",
                "job_id": job_state.get("job_id")
            }), 409

        current_job_id += 1
        active_id = current_job_id
        job_state["job_id"] = active_id

    worker = threading.Thread(
        target=run_scraping_worker,
        args=(active_id, query, pincode, in_stock_only),
        daemon=True
    )
    worker.start()

    return jsonify({
        "success": True,
        "message": "Oppo scraping job started",
        "query": query,
        "job_id": active_id,
        "pincode": pincode
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


@app.route("/api/export/csv", methods=["GET"])
@app.route("/api/export-csv", methods=["GET"])
def api_export_csv():
    """Stream clean CSV file of current scraped products."""
    csv_disk = os.path.join(SCRAPED_DIR, "oppo_products.csv")
    if os.path.exists(csv_disk):
        return send_file(
            csv_disk,
            mimetype="text/csv",
            as_attachment=True,
            download_name="oppo_products.csv"
        )
    return jsonify({"error": "No CSV data available"}), 404


@app.route("/api/export/json", methods=["GET"])
@app.route("/api/export-json", methods=["GET"])
def api_export_json():
    """Download JSON dataset."""
    json_disk = os.path.join(SCRAPED_DIR, "oppo_products.json")
    if os.path.exists(json_disk):
        return send_file(
            json_disk,
            mimetype="application/json",
            as_attachment=True,
            download_name="oppo_products.json"
        )
    return jsonify({"error": "No JSON data available"}), 404


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Oppo Intelligence Scraper",
        "port": 5057,
        "timestamp": datetime.now().isoformat()
    })


# ---------------- Oppo Automation API Integration ----------------
backend_dir = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from unified_automation import attach_flask_automation_routes

attach_flask_automation_routes(app, 'oppo')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5057))
    print(f"=====================================================")
    print(f"  Oppo Intelligence Pro Web Server Running")
    print(f"  Local API: http://localhost:{port}")
    print(f"  Status Endpoint: http://localhost:{port}/api/status")
    print(f"  Scrape Endpoint: http://localhost:{port}/api/scrape")
    print(f"  Automation Endpoint: http://localhost:{port}/api/automation/status")
    print(f"=====================================================")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

