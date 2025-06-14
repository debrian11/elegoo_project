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

    print(f"[SERVER] Waiting for client on port {PORT}")
    mac_con, mac_addr = pi_server.accept()
    print(f"[SERVER] Connected to {mac_addr}")
    mac_con.setblocking(False)

    last_sent = time.time() # storing current time without sleep()
    try:
        while True:
            current_time = time.time()
            read_socket, _, _ = select.select([mac_con], [], [], 0) # is the read_only socket ready to be read now
            if mac_con in read_socket: # if the mac_con is ready to be read in the read only socket...
                try:
                    mac_cmd = mac_con.recv(1024).decode().strip()
                    if mac_cmd:
                        print(f"[SERVER] Received: {mac_cmd}")
                        update_status(mac_cmd)
                        print(f"{status}")
                except BlockingIOError:
                    pass


            if current_time - last_sent >= 0.05:
                #pi_msg = f"\033[2A\033[Kstatus: {status}\n\033[K\n"
                pi_msg = f"status: {status}\n"

                try:
                    mac_con.sendall(pi_msg.encode())
                except BrokenPipeError:
                    print("[SERVER] Client disconnected")
                    break
                last_sent = current_time

    finally:
        mac_con.close()
        pi_server.close()

if __name__ == "__main__":
    main()
