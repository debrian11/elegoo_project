import socket
import time
import select

HOST = ''
PORT = 9000

status = "Servo: S_STOP | Motor: STOP | in: 100"

def update_status(cmd):
    global status
    if cmd == 'f':
        status = "Servo: S_STOP | Motor: FORWARD | in: 95"
    elif cmd == 'b':
        status = "Servo: S_STOP | Motor: BACKWARD | in: 120"
    elif cmd == 'l':
        status = "Servo: S_STOP | Motor: LEFT | in: 75"
    elif cmd == 'r':
        status = "Servo: S_STOP | Motor: RIGHT | in: 80"
    elif cmd == 's':
        status = "Servo: S_STOP | Motor: STOP | in: 100"
    elif cmd == 'z':
        status = "Servo: SWEEP | Motor: STOP | in: 100"
    else:
        status = f"Unknown command: {cmd}"

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    print(f"[MOCK SERVER] Waiting for TCP client on port {PORT}...")
    conn, addr = server_socket.accept()
    conn.setblocking(False)
    print(f"[MOCK SERVER] Connected by {addr}")

    last_sent = 0
    try:
        while True:
            now = time.time()

            # Receive command input
            try:
                ready, _, _ = select.select([conn], [], [], 0)
                if conn in ready:
                    cmd = conn.recv(1024).decode('utf-8').strip()
                    if cmd:
                        print(f"[MOCK SERVER] Got command: {cmd}")
                        update_status(cmd)
            except:
                pass

            # Send mock status every 0.05s
            if now - last_sent >= 0.05:
                msg = f"\033[2A\033[KStatus: {status}\n\033[K\n"
                try:
                    conn.sendall(msg.encode('utf-8'))
                    last_sent = now
                except BrokenPipeError:
                    print("[MOCK SERVER] Client disconnected.")
                    break

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Shutting down mock server.")
    finally:
        conn.close()
        server_socket.close()

if __name__ == "__main__":
    main()
