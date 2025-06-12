#!/usr/bin/env python3
# ---------- FOR THE PI (server)------------------#
# Keep this at the top of every new socket script you write — it’s your minimum server boilerplate.
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Create a TCP socket for IPv4
# Create a new socket object (virtual network port); # “Make me a device (object) that can listen for phone calls over IPv4 and talk like a landline.”
# AF_INET = Address Family for IpV4. I want to use IPv4 Addresses.
# AF_INET = Address family for IpV6.
# SOCK_STREAM = I want a TCP Connection.
# SOCK_DGRAM = I want a UDP Connection
# ALl together = Give me a TCP socket that can speak IPv4

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Allow reuse of the port after program restarts (avoids "Address already in use" errors)
# “Let me re-bind this port quickly if I stop and restart the program"
# Without this, you sometimes OSError: [Errno 98] Address already in use after a crash or ctrl+c
# “Let go of this port faster when I restart.”

# Bind the socket to all network interfaces on port 9000
HOST = ''           # '' is shorthand for "0.0.0.0" (listen on all interfaces)
PORT = 9000         # You can pick any unused port > 1024
server_socket.bind((HOST, PORT))

# Start listening for incoming connections (max 1 client in queue)
server_socket.listen(1)

# Accept a single client (blocking until someone connects)
conn, addr = server_socket.accept()
print(f"Connected by {addr}")



# ---------- MAC side (client) ------------------#
import socket

# IP address of the server (e.g., your Raspberry Pi)
SERVER_IP = '192.168.0.63'   # PI IP
PORT = 9000                  # Same port the Pi is listening on

# Create a TCP socket for IPv4
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server (Pi)
client_socket.connect((SERVER_IP, PORT))
print(f"Connected to {SERVER_IP}:{PORT}")

# Send a command (example: 'f' for forward)
client_socket.sendall(b'f\n')

# Optionally, receive response
response = client_socket.recv(1024).decode('utf-8')
print(f"Received: {response}")

# Close connection when done
client_socket.close()
