import socket
import serial
import serial.tools.list_ports
import time
import select

# === SERIAL SETUP ===
ports = list(serial.tools.list_ports.comports())
arduino_port = None

for port in ports:
    if 'USB' in port.device or 'ttyACM' in port.device or 'ttyUSB' in port.device:
        arduino_port = port.device
        print(f"Found Arduino on {arduino_port}")
        break

if arduino_port is None:
    print("No Arduino found.")
    exit(1)

ser = serial.Serial(port=arduino_port, baudrate=115200, timeout=0)
time.sleep(2)

# === TCP SERVER SETUP ===
HOST = ''
PORT = 9000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Waiting for TCP client on port {PORT}...")

conn, addr = server_socket.accept()
conn.setblocking(False)
print(f"Connected by {addr}")

last_line = ""
available_cmds = "f b l r s z"
last_sent = 0

try:
    while True:
        now = time.time()

        # Read and flush all serial input
        while ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                last_line = line

        # Handle TCP client input
        try:
            ready_to_read, _, _ = select.select([conn], [], [], 0)
            if conn in ready_to_read:
                cmd = conn.recv(1024).decode('utf-8').strip()
                if cmd:
                    ser.write((cmd + '\n').encode('utf-8'))
        except:
            pass

        # Send update every 0.05s
        if now - last_sent >= 0.05:
            msg = f"\033[2A\033[KStatus: {last_line}\n\033[KAvailable Commands: {available_cmds}\n"
            try:
                conn.sendall(msg.encode('utf-8'))
            except BrokenPipeError:
                print("Client disconnected.")
                break
            last_sent = now

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Shutting down.")

finally:
    ser.close()
    conn.close()
    server_socket.close()
