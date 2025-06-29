#!/usr/bin/env python3

# 6/22/2025
# This pi python scripts takes 3.0.0.0 and adds arduino nano detection.

import time
import socket
import select
import serial
import json
import serial.tools.list_ports
import os
from modules.pi_stream_video_usb import pi_video_stream

print("Starting PI_SERIAL stuff shortly!!")
time.sleep(2)

# ----- Global Variables ---- #
LAST_LINE_ARDUINO_JSON = ""
LAST_CMD_SENT_TO_ARDUINO = ""
LAST_CMD_TIME = 0
CMD_RESEND_INTERVAL = 0.2  # seconds
LAST_SENT = 0
STOP_JSON = {"L_DIR": 1, "R_DIR": 1, "L_PWM": 0, "R_PWM": 0, "S_SWEEP": 0}
TURNING = False
TURN_THRESHOLD = 15  # cm
LAST_NON_TURN_CMD = STOP_JSON
servo_sweep_status = 0

# ====================== SERIAL SETUP ==============================================================================================================
ELEGOO_PORT = '/dev/arduino_elegoo'
NANO_PORT = '/dev/arduino_nano'

# Check for Arduino Elegoo connection
while not os.path.exists(ELEGOO_PORT):
    print("No ELEGOO found. Retrying...")
    time.sleep(1)

print(f"(1) Connected to ELEGOO at {ELEGOO_PORT}")
PI_ELEGOO_PORT = serial.Serial(port=ELEGOO_PORT, baudrate=115200, timeout=1)
time.sleep(2)
PI_ELEGOO_PORT.write((json.dumps(STOP_JSON) + '\n').encode('utf-8'))

# Check for Arduino Nano connection
while not os.path.exists(NANO_PORT):
    print("No NANO found. Retrying...")
    time.sleep(1)

print(f"(1) Connected to NANO at {NANO_PORT}")
PI_NANO_PORT = serial.Serial(port=NANO_PORT, baudrate=115200, timeout=1)
time.sleep(2)

# ====================== TCP Setup ==============================================================================================================
HOST = ''
PORT = 9000
print(f"(2) Opening TCP socket for Client at {PORT}")
pi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pi_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
pi_socket.bind((HOST, PORT))
pi_socket.listen(1)
print(f"(3) Start the Macbook side of things please")

mac_con, mac_addr = pi_socket.accept()
mac_con.setblocking(False)
mac_connected = True
print(f"Connect by {mac_addr}")

# ====================== Start video stream ========================================================================================
if os.path.exists('/dev/video0'):
    print("Camera connected, starting stream")
    stream_video = pi_video_stream()
else:
    print("No camera connected at /dev/video0, skipping video stream")

# ====================== LOOP ==============================================================================================================
try:
    while True:
        CURRENT_TIME = time.time()
        # -----------------------------------------ARDUINO to PI----------------------------------------------------
        if PI_ELEGOO_PORT.in_waiting:
            JSON_INPUT_ARDUINO = PI_ELEGOO_PORT.readline().decode('utf-8', errors='ignore').strip() # Arduino string that looks like a json
            
            if JSON_INPUT_ARDUINO:
                try:
                    arduino_data = json.loads(JSON_INPUT_ARDUINO) # parses string into a dictionary
                    L_MRT_DATA = arduino_data.get("L_motor", "N/A")
                    R_MRT_DATA = arduino_data.get("R_motor", "N/A")
                    DIST_DATA = arduino_data.get("distance", "N/A")
                    TIME_DATA = arduino_data.get("time", "N/A")
                    LAST_LINE_ARDUINO_JSON = JSON_INPUT_ARDUINO # string. not a python dictionary
                    print_arduino_json = json.dumps(LAST_LINE_ARDUINO_JSON)
                    print(print_arduino_json)

                    # Ultrasonic sensor check
                    if DIST_DATA >= 0 and isinstance(DIST_DATA, int):
                        if DIST_DATA < TURN_THRESHOLD:
                            if not TURNING:
                                print("[PI] Obstacle detected — STARTING TURN")
                                turn_cmd = {"L_DIR": 1, "R_DIR": 1, "L_PWM": 100, "R_PWM": 0, "S_SWEEP": 1}
                                PI_ELEGOO_PORT.write((json.dumps(turn_cmd) + '\n').encode('utf-8'))
                                LAST_CMD_SENT_TO_ARDUINO = json.dumps(turn_cmd)
                                LAST_CMD_TIME = CURRENT_TIME
                                TURNING = True
                        else:
                            if TURNING:
                                print("[PI] Path clear — RESUMING LAST CMD")
                                if LAST_NON_TURN_CMD:
                                    PI_ELEGOO_PORT.write((json.dumps(LAST_NON_TURN_CMD) + '\n').encode('utf-8'))
                                    LAST_CMD_SENT_TO_ARDUINO = LAST_NON_TURN_CMD
                                    LAST_CMD_TIME = CURRENT_TIME
                                TURNING = False

                except json.JSONDecodeError:
                    print(f"[ERROR] Bad JSON: {JSON_INPUT_ARDUINO} '\n")

        # ------------------------------------------PI to ARDUINO---------------------------------------------------
        pi_read_socket, _, _ = select.select([mac_con], [], [], 0)
        if mac_con in pi_read_socket:
            try:
                # Take command from the mac and send it to the Arduino
                mac_cmd = mac_con.recv(1024).decode('utf-8').strip()
                if mac_cmd == "":
                    raise ConnectionResetError
                #PI_ELEGOO_PORT.write((mac_cmd + '\n').encode('utf-8'))
                PI_ELEGOO_PORT.write((mac_cmd + '\n').encode('utf-8'))
                LAST_CMD_SENT_TO_ARDUINO = mac_cmd
                LAST_NON_TURN_CMD = mac_cmd
                LAST_CMD_TIME = CURRENT_TIME

            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                mac_connected = False
                print("[MAC] Disconnected")
                print('STOPPING MOTORS')
                PI_ELEGOO_PORT.write((json.dumps(STOP_JSON) + '\n').encode('utf-8'))
                if os.path.exists('/dev/video0'):
                    if stream_video.poll() is None: # Check if it is still running
                        print("Stopping video stream")
                        stream_video.terminate()
        # ------------------------------------------- PI to MAC------------------------------------------------
        # Periodically send the Arduino data to the Mac for GUI display
        if CURRENT_TIME - LAST_SENT >= 0.05:
            mac_con.sendall((LAST_LINE_ARDUINO_JSON + '\n').encode('utf-8'))
            LAST_SENT = CURRENT_TIME

        # ---------------------------------------------------------------------------------------------
        # RESEND LAST CMD TO ARDUINO IF IDLE
        if CURRENT_TIME - LAST_CMD_TIME > CMD_RESEND_INTERVAL:
            if LAST_CMD_SENT_TO_ARDUINO:
                PI_ELEGOO_PORT.write((LAST_CMD_SENT_TO_ARDUINO + '\n').encode('utf-8'))
                LAST_CMD_TIME = CURRENT_TIME

except KeyboardInterrupt:
    print("\nShutting down.")

finally:
    PI_ELEGOO_PORT.close()
    mac_con.close()
    pi_socket.close()
    if os.path.exists('/dev/video0'):
        if stream_video.poll() is None: # Check if it is still running
            stream_video.terminate()
            stream_video.wait()   
