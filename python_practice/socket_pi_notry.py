# socket_pi.py

import socket
import select
import time

HOST = ''
PORT = 9000

status = "Servo: S_STOP | Motor: STOP | in: 100"

def update_status(mac_cmd):
    global status
    if mac_cmd == 'f':
        status = "Servo: S_STOP | Motor: FORWARD | in: 95"
    elif mac_cmd == 'b':
        status = "Servo: S_STOP | Motor: BACKWARD | in: 120"
    elif mac_cmd == 'l':
        status = "Servo: S_STOP | Motor: LEFT | in: 75"
    elif mac_cmd == 'r':
        status = "Servo: S_STOP | Motor: RIGHT | in: 80"
    elif mac_cmd == 's':
        status = "Servo: S_STOP | Motor: STOP | in: 100"
    elif mac_cmd == 'z':
        status = "Servo: SWEEP | Motor: STOP | in: 100"
    else:
        status = f"Unknown command: {mac_cmd}"

def main():
    pi_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pi_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    pi_server.bind((HOST, PORT))
    pi_server.listen(1)

    print(f"[PI] Waiting for client on port {PORT}")
    mac_con, mac_addr = pi_server.accept()
    print(f"[PI] Connected to {mac_addr}")
    mac_con.setblocking(False)

    last_sent = time.time()

    while True:
        current_time = time.time()

        # Read from Mac if ready
        read_ready, _, _ = select.select([mac_con], [], [], 0)
        if mac_con in read_ready:
            mac_cmd = mac_con.recv(1024).decode().strip()
            if mac_cmd:
                print(f"[PI] Received: {mac_cmd}")
                update_status(mac_cmd)
                print(f"{status}")

        # Send to Mac every 50ms
        if current_time - last_sent >= 0.05:
            pi_msg = f"status: {status}\n"
            mac_con.sendall(pi_msg.encode())
            last_sent = current_time

if __name__ == "__main__":
    main()
