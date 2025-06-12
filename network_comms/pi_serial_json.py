#!/usr/bin/env python3

import time
import socket
import select
import serial
import serial.tools.list_ports

# ====================== SERIAL SETUP ======================
ports = list(serial.tools.list_ports.comports())
ARDUINO_PORT = None

for port in ports:
    if 'USB' in port.device or 'ttyACM' in port.device or 'ttyUSB' in port.device or 'usb' in port.device:
        ARDUINO_PORT = port.device
        print(f"Found Arduino on {ARDUINO_PORT}")
        break

if ARDUINO_PORT is None:
    print("No Arduino found.")
    exit(1)

# Configures the serial port
ser = serial.Serial(port=ARDUINO_PORT, baudrate=115200, timeout=0)
time.sleep(2)

# ====================== TCP SERVER SETUP ======================
HOST = '' # this gets set to 0.0.0.0 which binds to all interfaces. Listen to TCP connections on any network interface
PORT = 9000

# Create a TCP socket for IPv4
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow reuse of the port after program restarts (avoids "Address already in use" errors)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

server_socket.bind((HOST, PORT)) # Bind the socket to all network interfaces (0.0.0.0 or '') on port 9000
server_socket.listen(1) # “Start listening for up to 1 incoming connection.”

print(f"Waiting for TCP client on port {PORT}...")

conn, addr = server_socket.accept() # Accept a single client (blocking until someone connects)
conn.setblocking(False)
print(f"Connected by {addr}")

LAST_LINE = ""
AVAILABLE_CMDS = "f b l r s z"
LAST_SENT = 0

# ====================== LOOP ======================

while True:
    now = time.time()

    while ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            LAST_LINE = line

    ready_to_read, _, _ = select.select([conn], [], [], 0)
    if conn in ready_to_read:
        cmd = conn.recv(1024).decode('utf-8').strip()
        if cmd:
            ser.write((cmd + '\n').encode('utf-8'))

    if now - LAST_SENT >= 0.05:
        MSG = f"\033[2A\033[KStatus: {LAST_LINE}\n\033[KAvailable Commands: {AVAILABLE_CMDS}\n"
        conn.sendall(MSG.encode('utf-8'))
        LAST_SENT = now

    time.sleep(0.01)
