# hardware_control.py

import RPi.GPIO as GPIO
import time
import requests
from device_state import device_status  

# Pin Map
LED_PINS = {
    "bedroom": 17,
    "living room": 27,
    "bathroom": 22
}

SERVO_PIN = 23

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup LED pins
for pin in LED_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Setup servo
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz
servo.start(0)

def update_dashboard(device, status):
    try:
        device_status[device] = status
        requests.post("http://localhost:5000/update", json={
            "device": device,
            "status": status
        })
    except Exception as e:
        print(f"❌ Failed to update dashboard: {e}")

def set_servo_angle(angle):
    duty = 2.5 + (angle / 180.0) * 10
    servo.ChangeDutyCycle(duty)
    time.sleep(2)
    servo.ChangeDutyCycle(0)

def handle_command(action, obj, location, others=""):
    print(f"[HARDWARE] Action: {action}, Object: {obj}, Location: {location}, Others: {others}")

    # 🔁 Normalize door commands
    if obj == "door":
        if action == "turn on":
            action = "open"
        elif action == "turn off":
            action = "close"

    # 💡 LIGHT CONTROL
    if action == "turn on" and obj == "light":
        if location in LED_PINS:
            GPIO.output(LED_PINS[location], GPIO.HIGH)
            update_dashboard(location, "on")
            print(f"💡 {location.capitalize()} light ON")

    elif action == "turn off" and obj == "light":
        if location in LED_PINS:
            GPIO.output(LED_PINS[location], GPIO.LOW)
            update_dashboard(location, "off")
            print(f"💡 {location.capitalize()} light OFF")

    # 🚪 DOOR CONTROL
    elif action == "open" and obj == "door":
        print("🚪 Opening door (servo to 85°)")
        update_dashboard("door", "open")
        set_servo_angle(85)

    elif action == "close" and obj == "door":
        print("🚪 Closing door (servo to 180°)")
        update_dashboard("door", "closed")
        set_servo_angle(180)

    else:
        print("⚠️ Unknown command")
