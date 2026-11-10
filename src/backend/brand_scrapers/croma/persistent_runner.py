#!/usr/bin/env python3
"""
Croma Intelligence Pro - 24/7 Persistent Supervisor & Multi-Tunnel Runner
Continuously runs both the FastAPI Web Server and Cloudflare Tunnel with automatic
process recovery, real-time public URL extraction, and automatic Localtunnel fallback.
"""

import os
import re
import sys
import time
import subprocess
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URL_FILE = os.path.join(BASE_DIR, "live_url.txt")
PORT = int(os.environ.get("PORT", 5054))

def run_server():
    """Keeps the FastAPI web server running continuously with automatic restarts."""
    while True:
        try:
            print(f"[SERVER] Starting Croma Intelligence Web Server on port {PORT}...")
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
    """Keeps public tunnel alive with Cloudflare and Localtunnel fallback."""
    cf_binary = os.path.join(BASE_DIR, "cloudflared.exe")
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    
    while True:
        rate_limited = False
        cf_available = os.path.exists(cf_binary)
        
        if cf_available:
            try:
                print(f"[TUNNEL] Requesting Cloudflare Quick Tunnel for port {PORT}...")
                p = subprocess.Popen(
                    [cf_binary, "tunnel", "--url", f"http://127.0.0.1:{PORT}", "--protocol", "http2"],
                    cwd=BASE_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1
                )
                
                for line in iter(p.stdout.readline, ''):
                    line_str = line.strip()
                    if not line_str:
                        continue
                    match = url_pattern.search(line_str)
                    if match:
                        live_url = match.group(0)
                        print("\n" + "="*70)
                        print("🔥 CROMA INTELLIGENCE PRO IS LIVE AT:")
                        print(f"👉 {live_url}")
                        print(f"👉 Local URL: http://localhost:{PORT}")
                        print("="*70 + "\n")
                        sys.stdout.flush()
                        with open(URL_FILE, "w", encoding="utf-8") as f:
                            f.write(live_url)
                    elif "429" in line_str or "provisioning failed" in line_str or "rate limit" in line_str.lower():
                        print("[TUNNEL RATE-LIMIT] Cloudflare quick-tunnel is rate limited (429). Falling back to Localtunnel...")
                        sys.stdout.flush()
                        rate_limited = True
                        try:
                            p.terminate()
                        except Exception:
                            pass
                        break
                p.wait()
            except Exception as e:
                print(f"[TUNNEL ERROR] {e}")
        else:
            print("[TUNNEL] cloudflared.exe not found. Proceeding directly to Localtunnel fallback...")
            rate_limited = True
        
        # Localtunnel fallback if Cloudflare is rate limited or unavailable
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
                        print("🔥 CROMA INTELLIGENCE PRO IS LIVE AT (Localtunnel):")
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
    print("   CROMA INTELLIGENCE PRO - 24/7 DUAL SUPERVISOR ENGINE")
    print("="*70)
    
    # Start web server thread
    t_server = threading.Thread(target=run_server, daemon=True)
    t_server.start()
    
    # Wait for server to bind port
    time.sleep(2)
    
    # Run tunnel on main thread
    run_tunnel()
