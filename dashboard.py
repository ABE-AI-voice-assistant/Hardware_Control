from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from device_state import device_status

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html', status=device_status)

@app.route('/update', methods=['POST'])
def update_status():
    data = request.get_json()
    device = data.get("device")
    status = data.get("status")

    if device in device_status:
        device_status[device] = status
        socketio.emit('status_update', {device: status})
        print(f"🔄 Updated {device} → {status}")

    return '', 200

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
