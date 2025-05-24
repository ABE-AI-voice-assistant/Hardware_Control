import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import os
from hardware_control import handle_command

BACKEND_URL = "https://final-year-production.up.railway.app/"

def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Mp3 files", "*.wav")])
    if not file_path:
        return

    try:
        with open(file_path, "rb") as f:
            files = {'audio': f}
            status_label.config(text="📤 Uploading...")
            root.update_idletasks()
            response = requests.post(BACKEND_URL, files=files)

        if response.status_code == 200:
            data = response.json()
            action = data.get("action")
            obj = data.get("object")
            others = data.get("others")

            handle_command(action, obj, others)

            result = f"✅ Action: {action}\nObject: {obj}\nOthers: {others}"
            status_label.config(text=result)
        else:
            status_label.config(text=f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# 🖼️ GUI Layout
root = tk.Tk()
root.title("Voice Command Tester")

root.geometry("400x250")
tk.Label(root, text="🎙️ Select a voice command (.wav):").pack(pady=20)

tk.Button(root, text="Browse & Send", command=upload_file).pack()

status_label = tk.Label(root, text="", wraplength=350, justify="left", fg="green")
status_label.pack(pady=30)

root.mainloop()
