"""
Apple Intelligence Pro - Asynchronous Background HTTP API Server & Automation Engine
Port: 5055
Serves live status polling, background scraping daemon, CSV/JSON export streaming,
and full Autonomous Bulk Buying Automation Bot with real-time zero-delay Chrome screen mirror.
"""

import os
import sys
import json
import re
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, send_file, Response
from flask_cors import CORS
from apple_scraper import AppleScraperEngine

# Ensure Windows terminal encoding does not crash on unicode / emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

app = Flask(__name__, static_folder="web")
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
DATA_DIR = os.path.join(BASE_DIR, "scraped_data")
AUTOMATION_DIR = r"C:\Users\DEBRAJ\Downloads\apple_automation\apple_automation"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

scraper_engine = AppleScraperEngine(data_dir=DATA_DIR)

# Global State for async scrape job tracking
job_state = {
    "status": "ready",
    "progress": 100,
    "current_query": "All",
    "pincode": "110058",
    "logs": [
        "Apple Intelligence Pro Scraper Engine Initialized.",
        "System Ready: Delivery fulfillment API & Exact-Model Isolation active."
    ],
    "products": [],
    "metrics": {
        "total_variants": 0,
        "in_stock_count": 0,
        "out_of_stock_count": 0,
        "deliverability_rate": 100.0,
        "min_price": 47600.0,
        "max_price": 184900.0,
        "avg_price": 98900.0,
        "min_model": "iPhone SE",
        "pincode": "110058"
    }
}
state_lock = threading.Lock()

# Global State for Apple Bulk Buying Automation Engine
automation_state = {
    "status": "idle",
    "current_step": 0,
    "progress": 0,
    "account": 1,
    "current_url": "https://www.apple.com/in/",
    "screenshot": None,
    "logs": [],
    "error": None,
    "notification": None
}
automation_lock = threading.Lock()


def log_automation(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] [{level}] {msg}"
    with automation_lock:
        automation_state["logs"].append(entry)
        if len(automation_state["logs"]) > 100:
            automation_state["logs"] = automation_state["logs"][-100:]
    try:
        # Safe ASCII sanitization to guarantee Windows console compatibility
        safe_entry = entry.encode("ascii", errors="replace").decode("ascii")
        print(f"[Apple Automation] {safe_entry}", flush=True)
    except Exception:
        pass


def safe_unlock_profile(account: int):
    try:
        from pathlib import Path
        p_dir = Path(AUTOMATION_DIR) / "chrome_profiles" / f"account_{account}"
        for name in ("SingletonLock", "SingletonSocket", "SingletonCookie", "lockfile"):
            f = p_dir / name
            if f.exists():
                try:
                    f.unlink(missing_ok=True)
                except Exception:
                    pass
    except Exception as e:
        print(f"safe_unlock_profile note: {e}")


def kill_account_chrome_if_locked(account: int):
    try:
        import subprocess
        ps_cmd = f"Get-CimInstance Win32_Process -Filter \"name = 'chrome.exe'\" | Where-Object {{ $_.CommandLine -like '*account_{account}*' }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force }}"
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=5, capture_output=True)
    except Exception:
        pass
    safe_unlock_profile(account)


def calculate_metrics(products, pincode="110058"):
    total = len(products)
    if total == 0:
        return {
            "total_variants": 0,
            "in_stock_count": 0,
            "out_of_stock_count": 0,
            "deliverability_rate": 0.0,
            "min_price": 0.0,
            "max_price": 0.0,
            "avg_price": 0.0,
            "min_model": "N/A",
            "pincode": pincode
        }

    in_stock = sum(1 for p in products if p.get("in_stock", True))
    out_of_stock = total - in_stock
    rate = round((in_stock / total) * 100, 1)

    prices = [p.get("price_num", 0.0) for p in products if p.get("price_num")]
    min_p = min(prices) if prices else 0.0
    max_p = max(prices) if prices else 0.0
    avg_p = round(sum(prices) / len(prices), 2) if prices else 0.0

    min_model = "iPhone SE"
    for p in products:
        if p.get("price_num") == min_p:
            min_model = p.get("model", "iPhone")
            break

    return {
        "total_variants": total,
        "in_stock_count": in_stock,
        "out_of_stock_count": out_of_stock,
        "deliverability_rate": rate,
        "min_price": min_p,
        "max_price": max_p,
        "avg_price": avg_p,
        "min_model": min_model,
        "pincode": pincode
    }


def load_initial_state():
    cached = scraper_engine.load_cached_products()
    if cached:
        with state_lock:
            job_state["products"] = cached
            job_state["metrics"] = calculate_metrics(cached)
            job_state["logs"].append(f"Loaded {len(cached)} authentic iPhone variants from storage.")


# ---------------- Scraper Endpoints ----------------

def background_scraper_task(query: str, pincode: str, in_stock_only: bool):
    with state_lock:
        job_state["status"] = "scraping"
        job_state["progress"] = 10
        job_state["current_query"] = query
        job_state["pincode"] = pincode
        job_state["logs"].append(f"Starting async scraper worker for query: '{query}', PIN: {pincode}")

    def progress_log(msg: str):
        with state_lock:
            job_state["logs"].append(msg)
            if len(job_state["logs"]) > 100:
                job_state["logs"] = job_state["logs"][-100:]
            if "Total authentic" in msg:
                job_state["progress"] = 35
            elif "Exact-Model" in msg:
                job_state["progress"] = 50
            elif "SKU" in msg:
                curr = job_state["progress"]
                if curr < 90:
                    job_state["progress"] = curr + 2

    try:
        results = scraper_engine.scrape_catalog(
            query=query,
            pincode=pincode,
            in_stock_only=in_stock_only,
            log_callback=progress_log
        )
        metrics = calculate_metrics(results, pincode)
        with state_lock:
            job_state["products"] = results
            job_state["metrics"] = metrics
            job_state["progress"] = 100
            job_state["status"] = "completed"
            job_state["logs"].append(f"Scrape completed successfully. {len(results)} variants verified and stored.")
    except Exception as e:
        with state_lock:
            job_state["status"] = "error"
            job_state["progress"] = 100
            job_state["logs"].append(f"Error during scrape execution: {str(e)}")


@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "All")
    pincode = data.get("pincode", "110058")
    in_stock_only = bool(data.get("in_stock_only", False))

    with state_lock:
        if job_state["status"] == "scraping":
            return jsonify({"status": "already_running", "message": "Scraper is currently executing a job."}), 409

    t = threading.Thread(target=background_scraper_task, args=(query, pincode, in_stock_only), daemon=True)
    t.start()
    return jsonify({"status": "started", "query": query, "pincode": pincode})


@app.route("/api/status", methods=["GET"])
def api_status():
    with state_lock:
        return jsonify({
            "status": job_state["status"],
            "progress": job_state["progress"],
            "current_query": job_state["current_query"],
            "pincode": job_state["pincode"],
            "logs": job_state["logs"],
            "metrics": job_state["metrics"],
            "products": job_state["products"]
        })


@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    csv_file = os.path.join(DATA_DIR, "apple_products.csv")
    if os.path.exists(csv_file):
        return send_file(csv_file, mimetype="text/csv", as_attachment=True, download_name="apple_products.csv")
    return jsonify({"error": "CSV dataset not found"}), 404


@app.route("/api/export/json", methods=["GET"])
def export_json():
    json_file = os.path.join(DATA_DIR, "apple_products.json")
    if os.path.exists(json_file):
        return send_file(json_file, mimetype="application/json", as_attachment=True, download_name="apple_products.json")
    return jsonify({"error": "JSON dataset not found"}), 404


# ---------------- Apple Automation API Integration ----------------
backend_dir = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from unified_automation import attach_flask_automation_routes

attach_flask_automation_routes(app, 'apple')


# ---------------- Static Web Serving ----------------

@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    if os.path.exists(os.path.join(WEB_DIR, path)):
        return send_from_directory(WEB_DIR, path)
    return send_from_directory(WEB_DIR, "index.html")


if __name__ == "__main__":
    load_initial_state()
    port = int(os.environ.get("PORT", 5055))
    print(f"Starting Apple Intelligence Pro API Server on http://127.0.0.1:{port}", flush=True)
    try:
        app.run(host="0.0.0.0", port=port, threaded=True, debug=False)
    except BaseException as e:
        import traceback
        traceback.print_exc()
        print(f"Server exited with: {type(e).__name__}: {e}", flush=True)
