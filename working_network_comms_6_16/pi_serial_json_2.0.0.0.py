#!/usr/bin/env python3

# 6/19/2025
# This pi python scripts reads the json from the arduino and sends to mac
# it reads the single character input from the mac gui and sends to the arduino
import time
import socket
import select
import serial
import json
import serial.tools.list_ports
import subprocess
from modules.pi_stream_video_usb import pi_video_stream

# ----- Flow ------ 
# 1) Connect to Arduino
# 2) Open TCP Socket to MAC
# 3) While Loop:
#   - Read Serial Data to Arduino
#   - Read TCP data from Mac
#   ---Send TCP serial data to the Pi
#   - Send TCP Data to Mac'
# -----Add stuff after here -----

print("Starting PI_SERIAL stuff shortly!!")
time.sleep(2)

# ====================== SERIAL SETUP ======================
ports = list(serial.tools.list_ports.comports())
ARDUINO_PORT = None

for port in ports:
    if 'USB' in port.device or 'ttyACM' in port.device or 'ttyUSB' in port.device or 'usb' in port.device:
        ARDUINO_PORT = port.device
        print(f"Connected to Arduino at {ARDUINO_PORT}")
        break

if ARDUINO_PORT is None:
    print("No Arduino found.")
    exit(1)

# Configures the serial port
PI_SERIAL_PORT = serial.Serial(port=ARDUINO_PORT, baudrate=115200, timeout=1)
time.sleep(2) # For arduino

# ====================== TCP Setup ======================
HOST = ''
PORT = 9000
print(f"Opening TCP socket for Client at {PORT}")
pi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pi_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
pi_socket.bind((HOST, PORT))
pi_socket.listen(1)
print(f"Start the Macbook side of things please")

mac_con, mac_addr = pi_socket.accept()
mac_con.setblocking(False)
mac_connected = True
print(f"Connect by {mac_addr}")

LAST_LINE_ARDUINO_JSON = ""
LAST_SENT = 0


# ====================== Start video stream ======================
print("Starting to stream video now")
stream_video = pi_video_stream()

# ====================== LOOP ======================
try:
    while True:
        CURRENT_TIME = time.time()

        # Arduino to Pi
        if PI_SERIAL_PORT.in_waiting:
            JSON_INPUT_ARDUINO = PI_SERIAL_PORT.readline().decode('utf-8', errors='ignore').strip()
            if JSON_INPUT_ARDUINO:
                try:
                    arduino_data = json.loads(JSON_INPUT_ARDUINO)
                    servo_data = arduino_data.get("servo", "N/A")
                    motor_data = arduino_data.get("motor", "N/A")
                    dist_data = arduino_data.get("distance", "N/A")
                    LAST_LINE_ARDUINO_JSON = JSON_INPUT_ARDUINO
                    print(f"Servo: {servo_data} | Motor: {motor_data} | Distance: {dist_data}")
                except json.JSONDecodeError:
                    print(f"[ERROR] Bad JSON: {JSON_INPUT_ARDUINO}")


        # Pi to Arduino
        pi_read_socket, _, _ = select.select([mac_con], [], [], 0)
        if mac_con in pi_read_socket:
            try:
                mac_cmd = mac_con.recv(1024).decode('utf-8').strip()
                if mac_cmd == "":
                    raise ConnectionResetError
                PI_SERIAL_PORT.write((mac_cmd + '\n').encode('utf-8'))
            
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                print("[MAC] Disconnected")
                mac_connected = False
                PI_SERIAL_PORT.write(b's\n')
                
                if stream_video.poll() is None: # Check if it is still running
                    print("Stopping video stream")
                    stream_video.terminate()
                    

        # Pi to Mac
        if CURRENT_TIME - LAST_SENT >= 0.05:
            mac_con.sendall((LAST_LINE_ARDUINO_JSON + '\n').encode('utf-8'))
            LAST_SENT = CURRENT_TIME

except KeyboardInterrupt:
    print("\nShutting down.")

finally:
    PI_SERIAL_PORT.close()
    mac_con.close()
    pi_socket.close()
    if stream_video.poll() is None: # Check if it is still running
        stream_video.terminate()
        stream_video.wait()

    