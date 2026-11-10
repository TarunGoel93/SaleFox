#!/usr/bin/env python3
"""
Root web_server.py entrypoint for SaleFox
Automatically starts the Flipkart Intelligence Scraper & Automation Server on Port 5051.
"""

import os
import sys

# Point working directory directly to Flipkart scraper backend
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FLIPKART_DIR = os.path.join(BASE_DIR, "src", "backend", "brand_scrapers", "flipkart")

if os.path.exists(FLIPKART_DIR):
    sys.path.insert(0, FLIPKART_DIR)
    os.chdir(FLIPKART_DIR)
    
    # Run the Flipkart server directly
    import web_server
    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5051))
        print("=" * 55)
        print(" 🚀 SaleFox Flipkart Intelligence Scraper Engine Active")
        print(f" Server Port:  {port}")
        print(f" Status URL:   http://localhost:{port}/api/status")
        print("=" * 55)
        web_server.app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
else:
    print(f"Error: Backend folder not found at {FLIPKART_DIR}")
