#!/usr/bin/env python3

# 6/28/2025
# This pi python scripts takes 3.0.0.0 and adds arduino nano detection.
# 6/29/2025 
# change json to include servo
# have explicity elegoo vs nano ports and commands
# 7/1/2025 
# add turn logic if sense left, turn right
# 7/10/2025, removed servo
# 7/19/2025, 

import time
import socket
import select
import serial
import json
import serial.tools.list_ports
import os
import csv
from modules.pi_stream_video_usb import pi_video_stream
from collections import OrderedDict

csv_log_file = open("nano_log.csv", "w", newline="")
csv_writer = csv.writer(csv_log_file)
csv_writer.writerow(["timestamp", "F_USS", "L_USS", "R_USS", "L_ENCD", "R_ENCD", "L_ENCD_COV", "R_ENCD_COV", "HEAD"])

print("Starting PI_SERIAL stuff shortly!!")
time.sleep(2)

# ----- Global Variables ---- #
STOP_JSON = {"L_DIR": 1, "R_DIR": 1, "L_PWM": 0, "R_PWM": 0}
LEFT_TURN = {"L_DIR": 0, "R_DIR": 1, "L_PWM": 65, "R_PWM": 65}
RIGHT_TURN = {"L_DIR": 1, "R_DIR": 0, "L_PWM": 65, "R_PWM": 65}
LAST_CMD_SENT_TO_ELEGO = json.dumps(STOP_JSON) #
LAST_NON_TURN_CMD =  json.dumps(STOP_JSON)
LAST_LINE_ELEGOO_JSON = ""
LAST_LINE_NANO_JSON = ""
LAST_CMD_TIME = 0 #
LAST_ELEGOO_SENT = 0
LAST_NANO_SENT = 0
START_TIME = time.time() #
START_TIME_DELAY = 10 #
TURNING = False
TURN_THRESHOLD = 5  # cm

TURN_START_TIME = 0
MIN_TURN_DURATION = 0.1  # seconds
CLEAR_THRESHOLD = 8

# Debounce (persistence) timers for each direction
LEFT_DETECTED, RIGHT_DETECTED, FRONT_DETECTED = False, False, False
LEFT_OBSTACLE_START_TIME, RIGHT_OBSTACLE_START_TIME, FRONT_OBSTACLE_START_TIME = 0, 0, 0

MIN_OBSTACLE_DURATION = 0.15  # seconds: obstacle must persist this long to trigger

CMD_ELEGOO_RESEND_INTERVAL = 0.2  # seconds #
TM_TIMING_NANO = 0.05 # seconds
TM_TIMING_ELEGOO = 0.06 # seconds

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
PI_ELEGOO_PORT.reset_input_buffer()

# Check for Arduino Nano connection
while not os.path.exists(NANO_PORT):
    print("No NANO found. Retrying...")
    time.sleep(1)

print(f"(1) Connected to NANO at {NANO_PORT}")
PI_NANO_PORT = serial.Serial(port=NANO_PORT, baudrate=115200, timeout=1)
time.sleep(2)
PI_NANO_PORT.reset_input_buffer() # Fllush serial port

# ====================== TCP Setup ==============================================================================================================
HOST = ''
PORT = 9000
print(f"(2) Opening TCP socket for Client at {PORT}")
pi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pi_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
pi_socket.bind((HOST, PORT))
pi_socket.listen(1)
print("(3) Start the Macbook side of things please")

mac_con, mac_addr = pi_socket.accept()
mac_con.setblocking(False)
mac_connected = True
print(f"Connect by {mac_addr}")
print("Waiting 2 seconds for Arduino sensors to stabilize...")
time.sleep(2)


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
                    # {"mssg_id":993,"F_USS":12,"L_USS":16,"R_USS":89,"L_ENCD":315,"R_ENCD":52}
                    NANO_MSSG_ID = NANO_JSON_DATA.get("mssg_id", "N/A")
                    HEADING = NANO_JSON_DATA.get("HEAD", "N/A")
                    F_USS = NANO_JSON_DATA.get("F_USS", "N/A")
                    L_USS = NANO_JSON_DATA.get("L_USS", "N/A")
                    R_USS = NANO_JSON_DATA.get("R_USS", "N/A")
                    L_ENCD = NANO_JSON_DATA.get("L_ENCD", "N/A")
                    R_ENCD = NANO_JSON_DATA.get("R_ENCD", "N/A")
                    LAST_LINE_NANO_JSON = JSON_INPUT_NANO # string. not a python dictionary
                    
                    # Print the json to the pi terminal locally to see mssg
                    #print_nano_json = json.dumps(LAST_LINE_NANO_JSON)

                    # Ultrasonic Check 2 ------------
                    if CURRENT_TIME - START_TIME < START_TIME_DELAY:
                        print("Skip initial sensor readings")
                    else:
                        if isinstance(F_USS, int) and isinstance(L_USS, int) and isinstance(R_USS, int):
                            MAX_TURN_DURATION = 0.7  # seconds
                            CLEAR_THRESHOLD_RELAXED = CLEAR_THRESHOLD - 2  # e.g., 6 instead of 8

                            if TURNING:
                                elapsed = CURRENT_TIME - TURN_START_TIME

                                if elapsed >= MIN_TURN_DURATION:
                                    # Relaxed check — makes it easier to escape the turn
                                    if (L_USS > CLEAR_THRESHOLD_RELAXED and 
                                        R_USS > CLEAR_THRESHOLD_RELAXED and 
                                        F_USS > CLEAR_THRESHOLD_RELAXED):
                                        print("[USS] CLEAR - RESUME LAST COMMAND")
                                        PI_ELEGOO_PORT.write((LAST_NON_TURN_CMD + '\n').encode('utf-8'))
                                        LAST_CMD_SENT_TO_ELEGO = LAST_NON_TURN_CMD
                                        LAST_CMD_TIME = CURRENT_TIME
                                        TURNING = False

                                    # Backup: hard timeout
                                    elif elapsed >= MAX_TURN_DURATION:
                                        print("[USS] FORCED RESUME - MAX TURN DURATION REACHED")
                                        PI_ELEGOO_PORT.write((LAST_NON_TURN_CMD + '\n').encode('utf-8'))
                                        LAST_CMD_SENT_TO_ELEGO = LAST_NON_TURN_CMD
                                        LAST_CMD_TIME = CURRENT_TIME
                                        TURNING = False

                            else:
                                # New turn condition (priority order: front, left, right)
                                if 0 <= F_USS < TURN_THRESHOLD:
                                    if L_USS > R_USS:
                                        print("[USS]: FRONT OBSTACLE: TURN LEFT")
                                        PI_ELEGOO_PORT.write((json.dumps(LEFT_TURN) + '\n').encode('utf-8'))
                                        LAST_CMD_SENT_TO_ELEGO = json.dumps(LEFT_TURN)
                                    else:
                                        print("[USS]: FRONT OBSTACLE: TURN RIGHT")
                                        PI_ELEGOO_PORT.write((json.dumps(RIGHT_TURN) + '\n').encode('utf-8'))
                                        LAST_CMD_SENT_TO_ELEGO = json.dumps(RIGHT_TURN)

                                    LAST_CMD_TIME = CURRENT_TIME
                                    TURNING = True
                                    TURN_START_TIME = CURRENT_TIME

                                elif 0 <= L_USS < TURN_THRESHOLD:
                                    print("[USS]: LEFT OBSTACLE: TURN RIGHT")
                                    PI_ELEGOO_PORT.write((json.dumps(RIGHT_TURN) + '\n').encode('utf-8'))
                                    LAST_CMD_SENT_TO_ELEGO = json.dumps(RIGHT_TURN)
                                    LAST_CMD_TIME = CURRENT_TIME
                                    TURNING = True
                                    TURN_START_TIME = CURRENT_TIME

                                elif 0 <= R_USS < TURN_THRESHOLD:
                                    print("[USS]: RIGHT OBSTACLE: TURN LEFT")
                                    PI_ELEGOO_PORT.write((json.dumps(LEFT_TURN) + '\n').encode('utf-8'))
                                    LAST_CMD_SENT_TO_ELEGO = json.dumps(LEFT_TURN)
                                    LAST_CMD_TIME = CURRENT_TIME
                                    TURNING = True
                                    TURN_START_TIME = CURRENT_TIME

                    # Heading PI check
                    #TBDDDDDDD

                except json.JSONDecodeError:
                    print(f"[ERROR] Bad JSON: {JSON_INPUT_NANO} '\n")

        # -----------------------------------------ELEGOO to PI----------------------------------------------------
        if PI_ELEGOO_PORT.in_waiting:
            JSON_INPUT_ELEGOO = PI_ELEGOO_PORT.readline().decode('utf-8', errors='ignore').strip() # Arduino string that looks like a json
            
            if JSON_INPUT_ELEGOO:
                try:
                    ELEGOO_JSON_DATA = json.loads(JSON_INPUT_ELEGOO) # parses string into a dictionary
                    # {"mssg_id":106,"L_motor":0,"R_motor":0}
                    ELEGOO_MSSG_ID = ELEGOO_JSON_DATA.get("mssg_id", "N/A")
                    L_MRT_DATA = ELEGOO_JSON_DATA.get("L_motor", "N/A")
                    R_MRT_DATA = ELEGOO_JSON_DATA.get("R_motor", "N/A")
                    LAST_LINE_ELEGOO_JSON = JSON_INPUT_ELEGOO # string. not a python dictionary

                    # Print the json to the pi terminal locally to see mssg
                    # print_elegoo_json = json.dumps(LAST_LINE_ELEGOO_JSON)                              

                except json.JSONDecodeError:
                    print(f"[ERROR] Bad JSON: {JSON_INPUT_ELEGOO} '\n")

        # ------------------------------------------MAC to PI to ELEGOO---------------------------------------------------
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
                # Log to CSV
                # Conversion factors from ticks to inches
                l_encd_ticks = NANO_DATA.get("L_ENCD", 0)
                r_encd_ticks = NANO_DATA.get("R_ENCD", 0)
                l_conv = l_encd_ticks / 9.4166 if isinstance(l_encd_ticks, int) else ""
                r_conv = r_encd_ticks / 9.333 if isinstance(r_encd_ticks, int) else ""

                csv_writer.writerow([
                    time.time(),
                    NANO_DATA.get("F_USS", ""),
                    NANO_DATA.get("L_USS", ""),
                    NANO_DATA.get("R_USS", ""),
                    l_encd_ticks,
                    r_encd_ticks,
                    l_conv,            # <-- new column
                    r_conv,            # <-- new column
                    NANO_DATA.get("HEAD", "")
                ])
                csv_log_file.flush()
                os.fsync(csv_log_file.fileno())


                # Reorder the json
                NANO_DATA_UPDATE = OrderedDict()
                NANO_DATA_UPDATE["source"] = "NANO" # first key
                NANO_DATA_UPDATE["time"] = time.time() # 2nd key
                NANO_DATA_UPDATE.update(NANO_DATA)
                mac_con.sendall((json.dumps(NANO_DATA_UPDATE) + '\n').encode('utf-8'))
                #print(f'NANO TO MAC: {NANO_DATA_UPDATE}')
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
                ELEGOO_DATA_UPDATE["time"] = time.time() # first key
                ELEGOO_DATA_UPDATE.update(ELEGOO_DATA)
                #print(f'ELEGOO TO MAC: {ELEGOO_DATA_UPDATE}')
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
    csv_log_file.close()
    if os.path.exists('/dev/video0'):
        if stream_video.poll() is None: # Check if it is still running
            stream_video.terminate()
            stream_video.wait()
