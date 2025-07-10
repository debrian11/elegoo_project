#!/usr/bin/env python3

# 6/19/2025
# This pi python scripts is used to test the Mac Gui with JSON now
# No Arduino is in the loop here

import time
import os
import socket
import select
import serial
import json
import serial.tools.list_ports
import subprocess
from modules.pi_stream_video_usb import pi_video_stream

print("Starting PI GUI Test stuff shortly!!")
time.sleep(2)

# ====================== SERIAL SETUP ======================
print("No Arduino to connect to for this test")

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

LAST_SENT = 0
last_mac_cmd_json = ""
ARDUINO_JSON_ELEGOO = {
    "mssg_id": 1000,
    "L_motor": 75,
    "R_motor": 60,
    "distance": 96,
    "S_angle": 40
}
ARDUINO_JSON_NANO = {
    "mssg_id": 1000,
    "L_ENCD": 6000,
    "R_ENCD": 5900
}


# ====================== Start video stream ======================
if os.path.exists('/dev/video0'):
    print("Camera connected, starting stream")
    stream_video = pi_video_stream()
else:
    print("No camera connected at /dev/video0, skipping video stream")

# ====================== LOOP ======================
try:
    while True:
        CURRENT_TIME = time.time()

        # Arduino to Pi

        # Pi to Arduino
        pi_read_socket, _, _ = select.select([mac_con], [], [], 0)
        if mac_con in pi_read_socket:
            try:
                mac_cmd_json = mac_con.recv(1024).decode().strip().split('\n')[0]

                if mac_cmd_json != last_mac_cmd_json:
                    try:
                        read_mac_json_data = json.loads(mac_cmd_json)
                        print(json.dumps(read_mac_json_data, indent=2))  # clean formatted output

                    
                    except json.JSONDecodeError:
                        print(f"[PI ERROR] Failed to parse: {mac_cmd_json}")
                        
                    last_mac_cmd_json = mac_cmd_json
            
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                print("TCP Disconnected")
                if os.path.exists('/dev/video0'):
                    if stream_video.poll() is None: # Check if it is still running
                        print("Stopping video stream")
                        stream_video.terminate()
                    
        # Pi to Mac
        # Periodically send the Arduino data to the Mac for GUI display
        
        # Pi to Mac (mock elegoo and nano)
        if CURRENT_TIME - LAST_SENT >= 0.05:
            ARDUINO_JSON_ELEGOO["mssg_id"] += 1
            ARDUINO_JSON_NANO["mssg_id"] += 1

            from collections import OrderedDict
            elegoo_out = OrderedDict()
            elegoo_out["source"] = "ELEGOO"
            elegoo_out["time"] = time.time()
            elegoo_out.update(ARDUINO_JSON_ELEGOO)

            nano_out = OrderedDict()
            nano_out["source"] = "NANO"
            nano_out["time"] = time.time()
            nano_out.update(ARDUINO_JSON_NANO)

            mac_con.sendall((json.dumps(elegoo_out) + '').encode('utf-8'))
            mac_con.sendall((json.dumps(nano_out) + '').encode('utf-8'))

            print(f"ELEGOO TO MAC: {elegoo_out}")
            print(f"NANO TO MAC: {nano_out}")
            LAST_SENT = CURRENT_TIME


except KeyboardInterrupt:
    print("\nShutting down.")

finally:
    mac_con.close()
    pi_socket.close()
    if os.path.exists('/dev/video0'):
        if stream_video.poll() is None: # Check if it is still running
            stream_video.terminate()
            stream_video.wait()