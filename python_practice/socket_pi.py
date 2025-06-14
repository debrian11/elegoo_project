#!/usr/bin/env python3
import socket
import time

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

HOST = ''           # '' is shorthand for "0.0.0.0" (listen on all interfaces)
PORT = 9000         # You can pick any unused port > 1024
my_socket.bind((HOST, PORT))
my_socket.listen(1)

# Accept a single client (blocking until someone connects)
print("Waiting for a connection")
mac_con, addr = my_socket.accept()
print(f"Connected by {mac_con} {addr}")

# Message portion here
try:
    while True:
        # Pi sends mssg to mac
        mac_con.sendall(b"msg from Pi\n") # sends and receives bytes (b) for sockets. not strings, hence the b
        time.sleep(1)

        # Pi reads reploy from Mac
        pi_data = mac_con.recv(1024) # max buffer size of 1024
        if not pi_data: # check if the socket sent is empty
            break
        print(f"Mac response is: {pi_data.decode().strip()}")
        # receives a byte so have to turn it into a string
        # the .strip removes the \n and spaces and tabs
except Exception as e: # Store the exception value as e then print it
    print(f"Error: {e}")

finally:
    mac_con.close()
    my_socket.close()
