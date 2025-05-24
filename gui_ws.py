# gui_ws.py

import tkinter as tk
import asyncio
import threading
import websockets
import json
from hardware_control import handle_command

WEBSOCKET_URL = "wss://final-year-production.up.railway.app/ws"

# -------- GUI setup --------
root = tk.Tk()
root.title("Voice Command Listener")
root.geometry("500x400")

status_label = tk.Label(root, text="Connecting to backend...", fg="blue")
status_label.pack(pady=10)

log_box = tk.Text(root, height=15, width=60, wrap="word")
log_box.pack(padx=10, pady=10)
log_box.insert(tk.END, "Waiting for commands...\n")

def log(msg):
    log_box.insert(tk.END, f"{msg}\n")
    log_box.see(tk.END)

# -------- WebSocket Listener --------
async def listen_to_ws():
    try:
        async with websockets.connect(WEBSOCKET_URL) as ws:
            status_label.config(text="✅ Connected to backend", fg="green")
            log("Listening for commands...")
            while True:
                msg = await ws.recv()
                data = json.loads(msg)

                # Safely get all expected fields
                action = data.get("action")
                obj = data.get("object")
                location = data.get("location", "")  # ✅ safe default
                others = data.get("others", "")      # ✅ safe default

                log(f"📥 Action: {action} | Object: {obj} | Location: {location}")
                handle_command(action, obj, location, others)

    except Exception as e:
        status_label.config(text="❌ Disconnected from backend", fg="red")
        log(f"[Error] {e}")

# -------- Run asyncio in a thread --------
def start_ws_thread():
    asyncio.run(listen_to_ws())

threading.Thread(target=start_ws_thread, daemon=True).start()

root.mainloop()
