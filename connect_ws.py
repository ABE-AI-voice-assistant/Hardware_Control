# connect_ws.py

import asyncio
import websockets
import json
from config import WEBSOCKET_URL
from hardware_control import handle_command

async def listen():
    print(f"🔌 Connecting to {WEBSOCKET_URL}")
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ Connected. Waiting for messages...")
        while True:
            try:
                msg = await ws.recv()
                print(f"📨 Message received: {msg}")
                data = json.loads(msg)
                
                action = data.get("action")
                obj = data.get("object")
                others = data.get("others")

                handle_command(action, obj, others)

            except Exception as e:
                print(f"❌ Error: {e}")
                break

if __name__ == "__main__":
    asyncio.run(listen())
