#!/usr/bin/env python3

# 6/22/2025
# This pi python scripts takes 2.0.0.0 and adds turning logic with object detection

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

# ====================== SERIAL SETUP ==============================================================================================================
ports = list(serial.tools.list_ports.comports())
ARDUINO_PORT = None

for port in ports:
    if 'USB' in port.device or 'ttyACM' in port.device or 'ttyUSB' in port.device or 'usb' in port.device:
        ARDUINO_PORT = port.device
        print(f"(1) Connected to Arduino at {ARDUINO_PORT}")
        break

if ARDUINO_PORT is None:
    print("No Arduino found.")
    exit(1)

# Configures the serial port
PI_SERIAL_PORT = serial.Serial(port=ARDUINO_PORT, baudrate=115200, timeout=1)
time.sleep(2) # For arduino

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

LAST_LINE_ARDUINO_JSON = ""
LAST_CMD_SENT_TO_ARDUINO = ""
LAST_CMD_TIME = 0
CMD_RESEND_INTERVAL = 0.2  # seconds
LAST_SENT = 0
STOP_JSON = {"L_DIR": 1, "R_DIR": 1, "L_PWM": 0, "R_PWM": 0, "S_SWEEP": 0}
TURNING = False
TURN_THRESHOLD = 15  # cm
LAST_NON_TURN_CMD = ""
servo_sweep_status = 0

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
        if PI_SERIAL_PORT.in_waiting:
            JSON_INPUT_ARDUINO = PI_SERIAL_PORT.readline().decode('utf-8', errors='ignore').strip()
            
            if JSON_INPUT_ARDUINO:
                try:
                    arduino_data = json.loads(JSON_INPUT_ARDUINO)
                    L_MRT_DATA = arduino_data.get("L_motor", "N/A")
                    R_MRT_DATA = arduino_data.get("R_motor", "N/A")
                    DIST_DATA = arduino_data.get("distance", "N/A")
                    TIME_DATA = arduino_data.get("time", "N/A")
                    LAST_LINE_ARDUINO_JSON = JSON_INPUT_ARDUINO
                    print_arduino_json = json.dumps(LAST_LINE_ARDUINO_JSON)
                    print(print_arduino_json)

                    # Ultrasonic sensor check
                    if DIST_DATA >= 0 and isinstance(DIST_DATA, int):
                        if DIST_DATA < TURN_THRESHOLD:
                            if not TURNING:
                                print("[PI] Obstacle detected — STARTING TURN")
                                turn_cmd = {"L_DIR": 1, "R_DIR": 1, "L_PWM": 100, "R_PWM": 0, "S_SWEEP": 1}
                                PI_SERIAL_PORT.write((json.dumps(turn_cmd) + '\n').encode('utf-8'))
                                LAST_CMD_SENT_TO_ARDUINO = json.dumps(turn_cmd)
                                LAST_CMD_TIME = CURRENT_TIME
                                TURNING = True
                        else:
                            if TURNING:
                                print("[PI] Path clear — RESUMING LAST CMD")
                                if LAST_NON_TURN_CMD:
                                    PI_SERIAL_PORT.write((LAST_NON_TURN_CMD + '\n').encode('utf-8'))
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
                #PI_SERIAL_PORT.write((mac_cmd + '\n').encode('utf-8'))
                PI_SERIAL_PORT.write((mac_cmd + '\n').encode('utf-8'))
                LAST_CMD_SENT_TO_ARDUINO = mac_cmd
                LAST_NON_TURN_CMD = mac_cmd
                LAST_CMD_TIME = CURRENT_TIME

            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                mac_connected = False
                print("[MAC] Disconnected")
                print('STOPPING MOTORS')
                PI_SERIAL_PORT.write((json.dumps(STOP_JSON) + '\n').encode('utf-8'))
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
                PI_SERIAL_PORT.write((LAST_CMD_SENT_TO_ARDUINO + '\n').encode('utf-8'))
                LAST_CMD_TIME = CURRENT_TIME

except KeyboardInterrupt:
    print("\nShutting down.")

finally:
    PI_SERIAL_PORT.close()
    mac_con.close()
    pi_socket.close()
    if os.path.exists('/dev/video0'):
        if stream_video.poll() is None: # Check if it is still running
            stream_video.terminate()
            stream_video.wait()   