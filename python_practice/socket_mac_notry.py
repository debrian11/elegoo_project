# socket_mac.py

import socket
import select

PI_IP = "192.168.0.63"
PORT = 9000

mac_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mac_socket.connect((PI_IP, PORT))
mac_socket.setblocking(False)

print("[MAC] Connected to Pi")

while True:
    # Read message if Pi sent one
    read_ready, _, _ = select.select([mac_socket], [], [], 0)
    if mac_socket in read_ready:
        pi_data = mac_socket.recv(1024).decode().strip()
        if pi_data:
            print(f"[MAC] Pi says: {pi_data}")

    # Ask user to send command
    user_input = input("Enter command (f/b/l/r/s/z): ").strip()
    if user_input:
        mac_socket.sendall((user_input + '\n').encode())
