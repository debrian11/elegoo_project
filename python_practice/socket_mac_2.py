import socket
import select

SERVER_IP = "192.168.0.63"
PORT = 9000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, PORT))
sock.setblocking(False)

print("[MAC] Connected to Pi.")

try:
    while True:
        # 🔄 Read incoming messages (non-blocking)
        ready, _, _ = select.select([sock], [], [], 0)
        if sock in ready:
            try:
                data = sock.recv(1024).decode().strip()
                if data:
                    #print(f"[MAC] Pi says: {data}")
                    print(f"[MAC] {data}", end='', flush=True)

            except BlockingIOError:
                pass

        # 🧠 User sends messages
        user_input = input("Send to Pi (or blank to skip): ").strip()
        if user_input:
            sock.sendall((user_input + "\n").encode())

except KeyboardInterrupt:
    print("Disconnected.")
finally:
    sock.close()
