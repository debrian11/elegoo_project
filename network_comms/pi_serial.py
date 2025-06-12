import time                     # For time tracking and sleeping
import socket                   # For TCP server
import select                   # For non-blocking I/O readiness checking
import serial                   # For serial communication with Arduino
import serial.tools.list_ports  # For listing all serial ports


# === SERIAL SETUP ===
ports = list(serial.tools.list_ports.comports())  # Get a list of all available serial ports
ARDUINO_PORT = None                               # Placeholder for the detected Arduino port

# Loop through ports to find something that looks like an Arduino
for port in ports:
    if 'USB' in port.device or 'ttyACM' in port.device or 'ttyUSB' in port.device:
        ARDUINO_PORT = port.device               # Save the matching device path
        print(f"Found Arduino on {ARDUINO_PORT}")
        break

# If no Arduino was found, exit the program
if ARDUINO_PORT is None:
    print("No Arduino found.")
    exit(1)

# Open the serial port to the Arduino
ser = serial.Serial(port=ARDUINO_PORT, baudrate=115200, timeout=0)
time.sleep(2)  # Let Arduino reset after opening the port

# === TCP SERVER SETUP ===
HOST = ''                  # Listen on all interfaces (e.g., Pi’s IP)
PORT = 9000                # Chosen TCP port for Mac to connect to

# Create TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow quick restart

# Bind socket to IP and port
server_socket.bind((HOST, PORT))
server_socket.listen(1)    # Listen for 1 connection (you only expect 1 Mac client)
print(f"Waiting for TCP client on port {PORT}...")

# Accept client connection
conn, addr = server_socket.accept()   # Blocks until a client connects
conn.setblocking(False)              # Don't freeze if client doesn't send data
print(f"Connected by {addr}")

LAST_LINE = ""                      # Stores most recent message from Arduino
AVAILABLE_CMDS = "f b l r s z"      # Help text for client
LAST_SENT = 0                       # Time tracker for 0.05s status updates

try:
    while True:
        now = time.time()  # Get current time for timing logic

        # Read and flush all serial input
        while ser.in_waiting:   # While there's data waiting in serial buffer...
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                LAST_LINE = line  # Save most recent message

        # Handle TCP client input
        try:
            ready_to_read, _, _ = select.select([conn], [], [], 0)  # Check if there's input
            if conn in ready_to_read:
                cmd = conn.recv(1024).decode('utf-8').strip()       # Get full command
                if cmd:
                    ser.write((cmd + '\n').encode('utf-8'))         # Send it to Arduino
        except:
            pass  # Ignore errors (client might have disconnected mid-read)

        # Send update every 0.05s
        if now - LAST_SENT >= 0.05:
            # ANSI codes move cursor up 2 lines, clear lines, and print fresh
            MSG = f"\033[2A\033[KStatus: {LAST_LINE}\n\033[KAvailable Commands: {AVAILABLE_CMDS}\n"
            try:
                conn.sendall(MSG.encode('utf-8'))  # Send it to the Mac
            except BrokenPipeError:
                print("Client disconnected.")      # If Mac disconnects, exit
                break
            LAST_SENT = now                        # Update LAST_SENT timer

        time.sleep(0.01)  # Pause for 10ms to prevent 100% cpu usage

except KeyboardInterrupt:
    print("Shutting down.")

finally:
    ser.close()              # Close serial port
    conn.close()             # Close TCP connection
    server_socket.close()    # Close server socket
