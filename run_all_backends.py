#!/usr/bin/env python3
"""
Master Launcher for All SaleFox Backend Intelligence Scrapers & Bot Servers.
Starts all 9 brand scrapers concurrently in a single terminal.
Press Ctrl+C to terminate all servers gracefully.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCRAPERS_DIR = BASE_DIR / "src" / "backend" / "brand_scrapers"

SERVICES = [
    {"name": "Amazon",   "port": 5050, "dir": SCRAPERS_DIR / "amazon"},
    {"name": "Flipkart", "port": 5051, "dir": SCRAPERS_DIR / "flipkart"},
    {"name": "Vivo",     "port": 5052, "dir": SCRAPERS_DIR / "vivo"},
    {"name": "Samsung",  "port": 5053, "dir": SCRAPERS_DIR / "samsung"},
    {"name": "Croma",    "port": 5054, "dir": SCRAPERS_DIR / "croma"},
    {"name": "Apple",    "port": 5055, "dir": SCRAPERS_DIR / "apple"},
    {"name": "Reliance", "port": 5056, "dir": SCRAPERS_DIR / "reliance"},
    {"name": "Oppo",     "port": 5057, "dir": SCRAPERS_DIR / "oppo"},
    {"name": "JioMart",  "port": 5062, "dir": SCRAPERS_DIR / "jiomart"},
]

def main():
    print("=" * 65)
    print(" 🚀 STARTING ALL 9 SALEFOX BRAND SCRAPERS & AUTOMATION SERVERS")
    print("=" * 65)

    processes = []
    py_exec = sys.executable

    for svc in SERVICES:
        server_py = svc["dir"] / "web_server.py"
        if not server_py.exists():
            print(f" [!] Missing: {svc['name']} at {server_py}")
            continue

        env = os.environ.copy()
        env["PORT"] = str(svc["port"])
        env["PYTHONUNBUFFERED"] = "1"

        proc = subprocess.Popen(
            [py_exec, "web_server.py"],
            cwd=str(svc["dir"]),
            env=env
        )
        processes.append((svc, proc))
        print(f"  ✓ [{svc['name']:<8}] Started on Port {svc['port']} (PID: {proc.pid})")
        time.sleep(0.3)

    print("=" * 65)
    print(" ✅ ALL BACKEND SERVERS ARE ACTIVE AND LISTENING!")
    print(" Press Ctrl+C in this terminal to stop all servers.")
    print("=" * 65)

    try:
        while True:
            time.sleep(1)
            for svc, p in processes:
                ret = p.poll()
                if ret is not None:
                    print(f" [!] {svc['name']} server exited with code {ret}")
    except KeyboardInterrupt:
        print("\nStopping all backend servers...")
        for svc, p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        print("All servers stopped successfully.")

if __name__ == "__main__":
    main()

