#!/usr/bin/env python3
"""
Flipkart Intelligence Scraper Web Server
Provides a modern REST API for live Flipkart catalog scraping,
smart query parsing, and multi-channel integration on Port 5051.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS

from flipkart_scraper import FlipkartScraper, DataExporter, parse_natural_query

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "scraped_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CSV_FILE = DATA_DIR / "flipkart_products.csv"
JSON_FILE = DATA_DIR / "flipkart_products.json"

app = Flask(__name__)
CORS(app)
logger = logging.getLogger("FlipkartWebServer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Global Scraper State
current_job: Dict[str, Any] = {
    "status": "idle",
    "message": "Flipkart Scraper is ready.",
    "progress": 0,
    "current_page": 0,
    "total_pages": 1,
    "query": "",
    "parsed": {},
    "results": [],
    "products": [],
    "logs": [],
    "stats": {
        "total_found": 0,
        "in_stock": 0,
        "lowest_price": None,
        "avg_price": None,
        "max_discount": None,
    },
    "error": None,
}
job_lock = threading.Lock()


def load_initial_catalog():
    """Load pre-scraped products from disk into current_job if available."""
    if JSON_FILE.exists():
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    current_job["products"] = data
                    current_job["results"] = data
                    current_job["stats"]["total_found"] = len(data)
                    prices = [p["price_num"] for p in data if p.get("price_num")]
                    if prices:
                        current_job["stats"]["lowest_price"] = min(prices)
                        current_job["stats"]["avg_price"] = sum(prices) / len(prices)
                    logger.info(f"Loaded {len(data)} initial Flipkart products from {JSON_FILE}")
        except Exception as e:
            logger.warning(f"Could not load initial Flipkart products: {e}")


load_initial_catalog()


def log_event(msg: str):
    ts = time.strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    with job_lock:
        current_job["logs"].append(entry)
        if len(current_job["logs"]) > 200:
            current_job["logs"].pop(0)
    logger.info(msg)


def run_scraping_job(
    query: str,
    pages: int,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: bool = True,
):
    with job_lock:
        current_job["status"] = "running"
        current_job["progress"] = 10
        current_job["message"] = f"Parsing query '{query}'..."
        current_job["query"] = query
        current_job["error"] = None
        current_job["logs"] = []

    parsed = parse_natural_query(query)
    with job_lock:
        current_job["parsed"] = parsed
        current_job["progress"] = 25
        current_job["message"] = f"Searching Flipkart for '{parsed.get('search_term')}'..."

    log_event(f"Query parsed: search_term='{parsed.get('search_term')}', brand={parsed.get('target_brand')}, model={parsed.get('target_model')}")

    scraper = FlipkartScraper()
    try:
        results = scraper.scrape_catalog(
            query=query,
            pages=pages,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock_only,
        )

        with job_lock:
            current_job["progress"] = 80
            current_job["message"] = f"Extracted {len(results)} verified handsets from Flipkart..."

        # Save to disk
        DataExporter.to_json(results, JSON_FILE)
        DataExporter.to_csv(results, CSV_FILE)

        prices = [p["price_num"] for p in results if p.get("price_num")]
        with job_lock:
            current_job["status"] = "completed"
            current_job["progress"] = 100
            current_job["message"] = f"Flipkart search complete. Found {len(results)} products."
            current_job["results"] = results
            current_job["products"] = results
            current_job["stats"]["total_found"] = len(results)
            current_job["stats"]["in_stock"] = len(results)
            if prices:
                current_job["stats"]["lowest_price"] = min(prices)
                current_job["stats"]["avg_price"] = sum(prices) / len(prices)

        log_event(f"Finished scraping Flipkart. Retrieved {len(results)} valid handsets.")

    except Exception as e:
        logger.exception("Error during Flipkart scraping job")
        with job_lock:
            current_job["status"] = "error"
            current_job["error"] = str(e)
            current_job["message"] = f"Error: {e}"
        log_event(f"Scraper error: {e}")


@app.route("/api/status", methods=["GET"])
def get_status():
    with job_lock:
        response = dict(current_job)
        response["count"] = len(response.get("products", []))
    return jsonify(response)


@app.route("/api/scrape", methods=["POST"])
def start_scrape():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip() or request.args.get("query", "").strip()
    if not query:
        return jsonify({"status": "error", "message": "Query parameter is required"}), 400

    pages = int(data.get("pages", 1) or request.args.get("pages", 1))
    min_price = data.get("min_price") or request.args.get("min_price")
    max_price = data.get("max_price") or request.args.get("max_price")
    in_stock_only = data.get("in_stock_only", True)

    if min_price is not None:
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = None

    if max_price is not None:
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = None

    # Check if a job is already actively running
    with job_lock:
        if current_job["status"] == "running":
            return jsonify({
                "status": "running",
                "message": "A Flipkart scraping job is already running.",
                "query": current_job.get("query"),
                "progress": current_job.get("progress"),
            }), 200

    thread = threading.Thread(
        target=run_scraping_job,
        args=(query, pages, min_price, max_price, in_stock_only),
        daemon=True,
    )
    thread.start()

    return jsonify({
        "status": "started",
        "message": f"Flipkart scraping started for '{query}'",
        "query": query,
    }), 200


@app.route("/api/products", methods=["GET"])
def get_products():
    with job_lock:
        prods = list(current_job.get("products", []))
    return jsonify({"products": prods, "count": len(prods)})


@app.route("/api/export-json", methods=["GET"])
def export_json():
    if JSON_FILE.exists():
        return send_file(str(JSON_FILE), mimetype="application/json", as_attachment=True, download_name="flipkart_products.json")
    with job_lock:
        return jsonify(current_job.get("products", []))


@app.route("/api/export-csv", methods=["GET"])
def export_csv():
    if CSV_FILE.exists():
        return send_file(str(CSV_FILE), mimetype="text/csv", as_attachment=True, download_name="flipkart_products.csv")
    return jsonify({"error": "CSV file not generated yet"}), 404


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "Flipkart Scraper", "port": 5051})


# ---------------- Flipkart Automation API Integration ----------------
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from unified_automation import attach_flask_automation_routes

attach_flask_automation_routes(app, "flipkart")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5051))
    print(f"==================================================")
    print(f" Flipkart Intelligence Scraper Engine Active")
    print(f" Server Port:  {port}")
    print(f" Status URL:   http://localhost:{port}/api/status")
    print(f" Scrape URL:   http://localhost:{port}/api/scrape")
    print(f"==================================================")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

