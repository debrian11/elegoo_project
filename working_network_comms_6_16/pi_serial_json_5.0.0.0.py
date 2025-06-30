#!/usr/bin/env python3

# 6/28/2025
# This pi python scripts takes 3.0.0.0 and adds arduino nano detection.
# 6/29/2025 
# change json to include servo
# have explicity elegoo vs nano ports and commands

import time
import socket
import select
import serial
import json
import serial.tools.list_ports
import os
from modules.pi_stream_video_usb import pi_video_stream
from collections import OrderedDict

print("Starting PI_SERIAL stuff shortly!!")
time.sleep(2)

# ----- Global Variables ---- #
STOP_JSON = {"L_DIR": 1, "R_DIR": 1, "L_PWM": 0, "R_PWM": 0, "S_SWEEP": 0}
LAST_CMD_SENT_TO_ELEGO = json.dumps(STOP_JSON)
LAST_NON_TURN_CMD =  json.dumps(STOP_JSON)
LAST_LINE_ELEGOO_JSON = ""
LAST_LINE_NANO_JSON = ""
LAST_CMD_TIME = 0
LAST_ELEGOO_SENT = 0
LAST_NANO_SENT = 0
TURNING = False
TURN_THRESHOLD = 15  # cm
CMD_ELEGOO_RESEND_INTERVAL = 0.2  # seconds
TM_TIMING_NANO = 0.200 # seconds
TM_TIMING_ELEGOO = 0.05 # seconds

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
        # -----------------------------------------NANO to PI----------------------------------------------------
        if PI_NANO_PORT.in_waiting:
            JSON_INPUT_NANO = PI_NANO_PORT.readline().decode('utf-8', errors='ignore').strip() # Arduino string that looks like a json
            
            if JSON_INPUT_NANO:
                try:
                    NANO_JSON_DATA = json.loads(JSON_INPUT_NANO) # parses string into a dictionary
                    # {"L_ENCD":0,"R_ENCD":0,"time":0}
                    L_ENCD = NANO_JSON_DATA.get("L_ENCD", "N/A")
                    R_ENCD = NANO_JSON_DATA.get("R_ENCD", "N/A")
                    TIME_DATA = NANO_JSON_DATA.get("time", "N/A")
                    LAST_LINE_NANO_JSON = JSON_INPUT_NANO # string. not a python dictionary
                    
                    # Print the json to the pi terminal locally to see mssg
                    print_nano_json = json.dumps(LAST_LINE_NANO_JSON)
                    #print(print_nano_json)

                except json.JSONDecodeError:
                    print(f"[ERROR] Bad JSON: {JSON_INPUT_NANO} '\n")

        # -----------------------------------------ELEGOO to PI----------------------------------------------------
        if PI_ELEGOO_PORT.in_waiting:
            JSON_INPUT_ELEGOO = PI_ELEGOO_PORT.readline().decode('utf-8', errors='ignore').strip() # Arduino string that looks like a json
            
            if JSON_INPUT_ELEGOO:
                try:
                    ELEGOO_JSON_DATA = json.loads(JSON_INPUT_ELEGOO) # parses string into a dictionary
                    # {"L_motor":0,"R_motor":0,"distance":91,"S_angle":55,"time":25686}
                    L_MRT_DATA = ELEGOO_JSON_DATA.get("L_motor", "N/A")
                    R_MRT_DATA = ELEGOO_JSON_DATA.get("R_motor", "N/A")
                    DIST_DATA = ELEGOO_JSON_DATA.get("distance", "N/A")
                    SERVO_DATA = ELEGOO_JSON_DATA.get("S_angle", "N/A")
                    TIME_DATA = ELEGOO_JSON_DATA.get("time", "N/A")
                    LAST_LINE_ELEGOO_JSON = JSON_INPUT_ELEGOO # string. not a python dictionary
                    
                    # Print the json to the pi terminal locally to see mssg
                    print_elegoo_json = json.dumps(LAST_LINE_ELEGOO_JSON)
                    #print(print_elegoo_json)

                    # Ultrasonic sensor check
                    if  isinstance(DIST_DATA, int) and DIST_DATA >= 0:
                        if DIST_DATA < TURN_THRESHOLD:
                            if not TURNING:
                                print("[PI] Obstacle detected — STARTING TURN")
                                turn_cmd = {"L_DIR": 1, "R_DIR": 1, "L_PWM": 100, "R_PWM": 0, "S_SWEEP": 1}
                                PI_ELEGOO_PORT.write((json.dumps(turn_cmd) + '\n').encode('utf-8'))
                                LAST_CMD_SENT_TO_ELEGO = json.dumps(turn_cmd)
                                LAST_CMD_TIME = CURRENT_TIME
                                TURNING = True
                        else:
                            if TURNING:
                                print("[PI] Path clear — RESUMING LAST CMD")
                                if LAST_NON_TURN_CMD:
                                    PI_ELEGOO_PORT.write((json.dumps(LAST_NON_TURN_CMD) + '\n').encode('utf-8'))
                                    LAST_CMD_SENT_TO_ELEGO = LAST_NON_TURN_CMD
                                    LAST_CMD_TIME = CURRENT_TIME
                                TURNING = False

                except json.JSONDecodeError:
                    print(f"[ERROR] Bad JSON: {JSON_INPUT_ELEGOO} '\n")

        # ------------------------------------------PI to ELEGOO---------------------------------------------------
        pi_read_socket, _, _ = select.select([mac_con], [], [], 0)
        if mac_con in pi_read_socket:
            try:
                # Take command from the mac and send it to the Arduino
                mac_cmd = mac_con.recv(1024).decode('utf-8').strip()
                if mac_cmd == "":
                    raise ConnectionResetError
                
                PI_ELEGOO_PORT.write((mac_cmd + '\n').encode('utf-8'))
                LAST_CMD_SENT_TO_ELEGO = mac_cmd
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

        # RESEND LAST CMD TO ARDUINO IF IDLE
        if CURRENT_TIME - LAST_CMD_TIME > CMD_ELEGOO_RESEND_INTERVAL:
            if LAST_CMD_SENT_TO_ELEGO:
                PI_ELEGOO_PORT.write((LAST_CMD_SENT_TO_ELEGO + '\n').encode('utf-8'))
                LAST_CMD_TIME = CURRENT_TIME

        # ------------------------------------------- PI to MAC (nano) ------------------------------------------------
        # Periodically send the Arduino data to the Mac for GUI display
        if CURRENT_TIME - LAST_NANO_SENT >= TM_TIMING_NANO:

            try:
                # Parse json from Elegoo then slap the "source:elegoo" in front of the json to send to mac
                NANO_DATA = json.loads(LAST_LINE_NANO_JSON)
                # Reorder the json
                NANO_DATA_UPDATE = OrderedDict()
                NANO_DATA_UPDATE["source"] = "NANO" # first key
                NANO_DATA_UPDATE.update(NANO_DATA)

                mac_con.sendall((json.dumps(NANO_DATA_UPDATE) + '\n').encode('utf-8'))
                print(f'NANO TO MAC: {NANO_DATA_UPDATE}')
            except json.JSONDecodeError:
                print("[ERROR] Failed to parse LAST_LINE_NANO_JSON to send")
    
            LAST_NANO_SENT = CURRENT_TIME

        # ------------------------------------------- PI to MAC (elegoo) ------------------------------------------------
        # Periodically send the Arduino data to the Mac for GUI display
        if CURRENT_TIME - LAST_ELEGOO_SENT >= TM_TIMING_ELEGOO:

            try:
                # Parse json from Elegoo then slap the "source:elegoo" in front of the json to send to mac
                ELEGOO_DATA = json.loads(LAST_LINE_ELEGOO_JSON)
                # Reorder the json
                ELEGOO_DATA_UPDATE = OrderedDict()
                ELEGOO_DATA_UPDATE["source"] = "ELEGOO" # first key
                ELEGOO_DATA_UPDATE.update(ELEGOO_DATA)
                print(f'ELEGOO TO MAC: {ELEGOO_DATA_UPDATE}')
                mac_con.sendall((json.dumps(ELEGOO_DATA_UPDATE) + '\n').encode('utf-8'))

            except json.JSONDecodeError:
                print("[ERROR] Failed to parse LAST_LINE_ELEGOO_JSON to send")
    
            LAST_ELEGOO_SENT = CURRENT_TIME


except KeyboardInterrupt:
    print("\nShutting down.")

finally:
    PI_ELEGOO_PORT.close()
    PI_NANO_PORT.close()
    mac_con.close()
    pi_socket.close()
    if os.path.exists('/dev/video0'):
        if stream_video.poll() is None: # Check if it is still running
            stream_video.terminate()
            stream_video.wait()
