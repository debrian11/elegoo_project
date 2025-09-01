# This is chatgpt code on Aug 7th i may use later

import serial
import json

class Robot:
    def __init__(self, motor_port, sensor_port, baudrate=9600):
        # Hardware connections
        self.motor_port = serial.Serial(motor_port, baudrate, timeout=1)
        self.sensor_port = serial.Serial(sensor_port, baudrate, timeout=1)

        # Robot state
        self.position = (0, 0)   # x, y in some grid
        self.heading = 0         # degrees
        self.map = {}            # {(x, y): "obstacle"/"clear"}
    
    # --- Sensor Methods ---
    def read_sensors(self):
        """Reads JSON data from sensor port (Nano)."""
        try:
            line = self.sensor_port.readline().decode().strip()
            if line:
                data = json.loads(line)
                self.heading = data.get("heading", self.heading)
                self.update_map(data)
                return data
        except json.JSONDecodeError:
            print("Bad sensor JSON:", line)
        return {}

    def update_map(self, sensor_data):
        """Update internal map from sensor data (stub)."""
        # For now just print; later update self.map
        print("Updating map with:", sensor_data)

    # --- Movement Methods ---
    def send_pwm(self, left_pwm, right_pwm):
        """Send PWM commands to the motor controller (Elegoo)."""
        msg = json.dumps({"left_pwm": left_pwm, "right_pwm": right_pwm})
        self.motor_port.write((msg + "\n").encode())

    def stop(self):
        self.send_pwm(0, 0)

    # --- Navigation (stub for now) ---
    def go_to(self, x, y):
        """Navigate to a coordinate (future A* implementation)."""
        print(f"Planning path from {self.position} to {(x, y)}")
        # Later: pathfinding algorithm here
        self.position = (x, y)

    # --- Map Sharing ---
    def export_map(self):
        return self.map

    def load_map(self, map_data):
        self.map = map_data
