import asyncio
import socketio
import json # For parsing commands if they ever come as strings
from config import WEBSOCKET_URL # e.g., "http://your-nestjs-server-ip:port"
# from hardware_control import handle_command

# Create an Async Socket.IO client instance
sio = socketio.AsyncClient(logger=True, engineio_logger=False) # Enable logging for debugging

# handle command can be in other file
def handleCommand (action,obj,location):
    if(action !=None):
        print("action",action)
    if(obj!=None):
        print("obj",obj)
    if(location !=None):
        print("location",location)
    pass


@sio.event
async def connect():
    print(f"✅ Connected to Socket.IO server. My SID: {sio.sid}")
    print("📢 Announcing myself as an available device...")
    await sio.emit('add-to-devices') 

@sio.on('connected')
async def on_connected_by_client(data):
    print(f"🤝 A client has connected to this device: {data}")

@sio.on('connection-failed')
async def on_connection_failed(data:str)->None:
    print(f"⚠️ Connection attempt failed: {data}")

@sio.on('message-from-connected-device')
async def on_message_from_client(data):
    #This is the main event for receiving commands from the paired client, forwarded by the server.
    print(f"📨 Command received: {data}")

    if isinstance(data, str):
        try:
            command_data = json.loads(data)
        except json.JSONDecodeError:
            print(f"❌ Error: Received non-JSON string message: {data}")
            return
    elif isinstance(data, dict):
        command_data = data # Assume it's already a dict
    else:
        print(f"❌ Error: Received unexpected data type for command: {type(data)} - {data}")
        return

    action = command_data.get("action")
    obj = command_data.get("object")
    location = command_data.get("location")

    try:
        handleCommand(action,obj,location)
    except Exception as e:
        print(f"❌ Error processing command '{action}': {e}")

retry_delay = 5
async def run_device_client():
    # Connects to the Socket.IO server and keeps the client running.
    print(f"🔌 Attempting to connect to Socket.IO server at {WEBSOCKET_URL}")
    try:
        await sio.connect(WEBSOCKET_URL, transports=['websocket'],
                          wait_timeout=10)
        await sio.wait() # Keep the client running and listening

    except socketio.exceptions.ConnectionError as e:
        print(f"❌ Socket.IO Connection Error: {e}. Retrying in {retry_delay} seconds...")
    except asyncio.CancelledError:
        print("🔌 Listener task cancelled.")
        return # Exit loop if cancelled
    except Exception as e:
        print(f"❌ An unexpected error occurred in run_device_client(): {e}. Retrying in {retry_delay} seconds...")
    finally:
        if sio.connected:
            print("🔌 Disconnecting due to error or shutdown...")
            await sio.disconnect()
    
    if not sio.connected: # If disconnected or connection failed
        await asyncio.sleep(retry_delay) # Wait before retrying


if __name__ == "__main__":
    try:
        asyncio.run(run_device_client())
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user. Exiting.")
    finally:
        # Ensure client is disconnected if asyncio.run was interrupted
        if sio.connected:
            print("Performing final disconnect...")
            async def final_disconnect():
                await sio.disconnect()
            try:
                asyncio.run(final_disconnect())
            except RuntimeError: # If loop is already closed
                 pass
            except Exception as e:
                print(f"Error during final disconnect: {e}")

