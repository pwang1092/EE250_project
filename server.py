from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# In-memory storage for current state
current_sensor_state = None
current_face_state = None

# POST endpoint to receive sound and light sensor data
@app.route('/api/sensors', methods=['POST'])
def handle_sensor_data():
    data = request.get_json()
    required_keys = ['ultrasonic_reading', 'light_level']

    # Check if the required keys exist in the posted data
    if not all(key in data for key in required_keys):
        return jsonify({'error': 'Missing required data'}), 400

    # Add a timestamp if it's not provided
    if 'timestamp' not in data:
        data['timestamp'] = datetime.utcnow().isoformat()

    # Store the current state
    global current_sensor_state
    current_sensor_state = data

    return jsonify({'message': 'Sensor data received successfully'}), 201

# POST endpoint to handle face detection flags
@app.route('/api/faces', methods=['POST'])
def handle_face_detection():
    data = request.get_json()
    required_keys = ['faces', 'image', 'timestamp']

    # Check if the required keys exist in the posted data
    if not all(key in data for key in required_keys):
        return jsonify({'error': 'Missing required data'}), 400

    # Add a timestamp if it's not provided
    if 'timestamp' not in data:
        data['timestamp'] = datetime.utcnow().isoformat()

    # Store the current state
    global current_face_state
    current_face_state = data

    return jsonify({'message': 'Face detection flag received successfully'}), 201

# Endpoint to fetch current sensor data
@app.route('/api/sensors', methods=['GET'])
def get_sensor_data():
    return jsonify(current_sensor_state)

# Endpoint to fetch current face detection data
@app.route('/api/faces', methods=['GET'])
def get_face_detection_data():
    return jsonify(current_face_state)

if __name__ == '__main__':
    app.run(debug=True)

