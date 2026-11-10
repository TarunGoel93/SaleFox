#!/usr/bin/env python3
"""
Samsung Intelligence Pro - 24/7 Persistent Supervisor & Tunnel Runner
Keeps the Web Server and Cloudflare Tunnel running continuously with automatic restarts,
captures the live public URL, and saves it to live_url.txt.
"""

import os
import re
import sys
import time
import subprocess
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URL_FILE = os.path.join(BASE_DIR, "live_url.txt")
PORT = int(os.environ.get("PORT", 5053))

def run_server():
    """Keeps the FastAPI web server alive."""
    while True:
        try:
            print(f"[SERVER] Starting Samsung Web Server on port {PORT}...")
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            p = subprocess.Popen(
                [sys.executable, "-u", os.path.join(BASE_DIR, "web_server.py")],
                cwd=BASE_DIR,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in p.stdout:
                line_str = line.strip()
                if line_str and "GET" not in line_str:
                    print(f"[SERVER] {line_str}")
            p.wait()
        except Exception as e:
            print(f"[SERVER ERROR] {e}")
        print("[SERVER] Web server exited. Restarting in 3 seconds...")
        time.sleep(3)

def run_tunnel():
    """Keeps the Cloudflare tunnel alive and saves live URL."""
    cf_binary = os.path.join(BASE_DIR, "cloudflared.exe")
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    
    while True:
        rate_limited = False
        try:
            print("[TUNNEL] Requesting Cloudflare Tunnel for port 5051...")
            p = subprocess.Popen(
                [cf_binary, "tunnel", "--url", f"http://127.0.0.1:{PORT}", "--protocol", "http2"],
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in p.stdout:
                line_str = line.strip()
                match = url_pattern.search(line_str)
                if match:
                    live_url = match.group(0)
                    print("\n" + "="*70)
                    print(f"🔥 SAMSUNG INTELLIGENCE PRO IS LIVE AT:")
                    print(f"👉 {live_url}")
                    print(f"👉 Local URL: http://localhost:{PORT}")
                    print("="*70 + "\n")
                    with open(URL_FILE, "w", encoding="utf-8") as f:
                        f.write(live_url)
                elif "429" in line_str or "provisioning failed" in line_str:
                    print(f"[TUNNEL RATE-LIMIT] Cloudflare quick-tunnel is rate limited (429). Falling back to Localtunnel...")
                    rate_limited = True
                    try:
                        p.terminate()
                    except Exception:
                        pass
                    break
            p.wait()
        except Exception as e:
            print(f"[TUNNEL ERROR] {e}")
        
        if rate_limited:
            try:
                print("[TUNNEL FALLBACK] Launching Localtunnel fallback...")
                lt_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.loca\.lt")
                lt_proc = subprocess.Popen(
                    ["cmd.exe", "/c", "npx", "-y", "localtunnel", "--port", str(PORT)],
                    cwd=BASE_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                for lt_line in lt_proc.stdout:
                    lt_line_str = lt_line.strip()
                    lt_match = lt_pattern.search(lt_line_str)
                    if lt_match:
                        lt_url = lt_match.group(0)
                        print("\n" + "="*70)
                        print(f"🔥 SAMSUNG INTELLIGENCE PRO IS LIVE AT (Localtunnel):")
                        print(f"👉 {lt_url}")
                        print(f"👉 Local URL: http://localhost:{PORT}")
                        print("="*70 + "\n")
                        with open(URL_FILE, "w", encoding="utf-8") as f:
                            f.write(lt_url)
                lt_proc.wait()
            except Exception as ex:
                print(f"[FALLBACK TUNNEL ERROR] {ex}")
        
        cooldown = 30 if rate_limited else 5
        print(f"[TUNNEL] Reconnecting in {cooldown} seconds...")
        time.sleep(cooldown)

if __name__ == "__main__":
    print("="*70)
    print("   SAMSUNG INTELLIGENCE PRO - 24/7 DUAL SUPERVISOR ENGINE")
    print("="*70)
    
    # Start server thread
    t_server = threading.Thread(target=run_server, daemon=True)
    t_server.start()
    
    # Wait for server to bind port
    time.sleep(2)
    
    # Run tunnel on main thread
    run_tunnel()
