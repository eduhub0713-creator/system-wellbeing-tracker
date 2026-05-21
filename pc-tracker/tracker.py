import ctypes
import time
import os
from datetime import datetime

user32 = ctypes.windll.user32

def get_active_window_title():
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    if length > 0:
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    return "Idle Desktop Environment"

def run_tracker():
    log_path = os.path.join(os.path.expanduser("~"), "system_telemetry_matrix.txt")
    last_window = ""
    start_time = time.time()

    while True:
        try:
            current_window = get_active_window_title()
            
            if current_window != last_window:
                end_time = time.time()
                duration = round(end_time - start_time)
                
                # Filter noise and record active windows
                if last_window and duration > 1:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    entry = f"[{timestamp}] WindowsNode | Process Focus: {last_window} | Active Runtime: {duration}s\n"
                    
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(entry)
                        
                last_window = current_window
                start_time = time.time()
                
            time.sleep(1)
        except Exception:
            pass

if __name__ == "__main__":
    # Suppress console visibility instantly on invocation
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window != 0:
        ctypes.windll.user32.ShowWindow(console_window, 0)
    run_tracker()