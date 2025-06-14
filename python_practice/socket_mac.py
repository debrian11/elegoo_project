#!/usr/bin/env python3
import socket
import time

# IP address of the server (e.g., your Raspberry Pi)
SERVER_IP = '192.168.0.63'   # PI IP
PORT = 9000                  # Same port the Pi is listening on

# Setup your tcp socket for IPv4on host
mac_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mac_socket.connect((SERVER_IP, PORT))

print(f"Connected to {SERVER_IP}:{PORT}")

try:
    while True:
        # Receive message from Pi
        mac_data = mac_socket.recv(1024)
        if not mac_data:
            break
        print(f"Pi says: {mac_data.decode().strip()}")

        # Type something to send back
        user_input = input("Send to Pi: ")
        mac_socket.sendall(user_input.encode())

except Exception as e:
    print(f"Error: {e}")
finally:
    mac_socket.close()
