from flask import Flask, render_template
from flask_mqtt import Mqtt
import re

app = Flask(__name__)

# MQTT Configuration
app.config['MQTT_BROKER_URL'] = 'localhost'  # Replace with your MQTT broker
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''  # Optional, leave empty for public brokers
app.config['MQTT_PASSWORD'] = ''  # Optional, leave empty for public brokers
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = False

mqtt = Mqtt(app)

capacity = 4  # Maximum number of parking spots

spots_available = capacity  # Initialize spots available as the full capacity


@app.route('/')
def index():
    return render_template('index.html', spots=spots_available)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker!")
    mqtt.subscribe('#')  # Subscribe to all topics for flexibility

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global spots_available
    payload = message.payload.decode().strip()  # Decode and clean the MQTT message
    print(f"Received message: {payload}")

    # Check if the message starts with "CARCOUNT-"
    if payload.startswith("CARCOUNT-"):
        try:
            # Extract the car count from the message
            car_count = int(payload.split('-')[1])
            spots_available = capacity - car_count  # Calculate spots available
            if spots_available < 0:
                spots_available = 0  # Ensure it doesn't go negative
            print(f"Updated spots_available to: {spots_available}")
        except (ValueError, IndexError) as e:
            # Log error for malformed messages
            print(f"Error processing CARCOUNT message: {payload}, Error: {e}")
    else:
        print(f"Unhandled message: {payload}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
