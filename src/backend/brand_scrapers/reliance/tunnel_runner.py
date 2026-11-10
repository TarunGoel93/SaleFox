"""
24/7 Persistent Reliance Digital Server & Cloudflare HTTP/2 Tunnel Runner
Automatically launches, monitors, and auto-heals:
1. web_server.py (Port 5050)
2. cloudflared tunnel
Saves active public URL to public_url.txt
"""

import subprocess
import re
import time
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARED = os.path.join(BASE_DIR, "cloudflared.exe")
URL_FILE = os.path.join(BASE_DIR, "public_url.txt")
PYTHON_EXE = sys.executable

def start_server():
    print("[*] Starting Reliance Digital Web Server (web_server.py)...")
    server_proc = subprocess.Popen(
        [PYTHON_EXE, "web_server.py"],
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="ignore"
    )
    return server_proc

def run():
    server = start_server()
    # Give server 2 seconds to bind to port 5050
    time.sleep(2)
    
    print(f"[*] Starting persistent 24/7 Cloudflare tunnel for http://127.0.0.1:5050...")
    while True:
        # Check if server process is still alive; restart if it died
        if server.poll() is not None:
            print("[!] Web server exited. Restarting web_server.py...")
            server = start_server()
            time.sleep(2)

        try:
            cmd = [CLOUDFLARED, "tunnel", "--url", "http://127.0.0.1:5050", "--protocol", "http2"]
            p = subprocess.Popen(
                cmd,
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="ignore"
            )
            
            for line in p.stdout:
                line_str = line.rstrip()
                print(line_str)
                m = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line_str)
                if m:
                    tunnel_url = m.group(0)
                    print("\n" + "="*60)
                    print(f" LIVE PUBLIC RELIANCE DIGITAL DASHBOARD URL: {tunnel_url}")
                    print("="*60 + "\n")
                    with open(URL_FILE, "w", encoding="utf-8") as f:
                        f.write(tunnel_url + "\n")

            p.wait()
            print("[!] Cloudflare tunnel disconnected. Reconnecting in 2 seconds...")
            time.sleep(2)
        except Exception as e:
            print(f"[!] Tunnel exception: {e}. Retrying in 3 seconds...")
            time.sleep(3)

if __name__ == "__main__":
    run()
