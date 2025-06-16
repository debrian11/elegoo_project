#!/usr/bin/env python3
import tkinter as tk           # For GUI creation
import socket                  # For TCP connection
import re                      # For stripping ANSI escape codes
import time                    # For timing connection health and speed

# === CONFIGURATION ===
PI_IP = "192.168.0.63"  # <-- Replace with your Pi's actual IP address
PORT = 9000             # This should match the port used by your Pi script

# === TCP CLIENT SETUP ===
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket
sock.connect((PI_IP, PORT))                               # Connect to the Pi
sock.setblocking(False)                                   # Non-blocking mode for async reads

# === GUI SETUP ===
root = tk.Tk()                     # Create the main window
root.title("Robot Status Dashboard")
root.geometry("600x280")          # Width x Height

# === GUI Labels ===
# Label showing last status from Arduino
status_label = tk.Label(root, text="Status: ...", font=("Courier", 16), anchor="w", justify="left")
status_label.pack(padx=10, pady=(20, 5), anchor="w")

# Label showing connection status
conn_label = tk.Label(root, text="Connection: ✅ Connected", font=("Courier", 14),
                      anchor="w", justify="left", fg="green")
conn_label.pack(padx=10, pady=(0, 5), anchor="w")

# Label showing data rate
rate_label = tk.Label(root, text="Transfer: -- B/s", font=("Courier", 12), anchor="w", justify="left")
rate_label.pack(padx=10, pady=(0, 5), anchor="w")

# === SEND COMMAND FUNCTION ===
def send_cmd(cmd):
    """Send a single-character command to the Pi over TCP."""
    try:
        sock.sendall((cmd + '\n').encode('utf-8'))
    except Exception as e:
        print(f"Send failed: {e}")

# === COMMAND BUTTONS SETUP ===
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# List of command characters and labels for buttons
commands = ['f', 'b', 'l', 'r', 's', 'z']
labels = ['Forward', 'Backward', 'Left', 'Right', 'Stop', 'Sweep']

# Create buttons for each command
for i, (cmd, label) in enumerate(zip(commands, labels)):
    btn = tk.Button(button_frame, text=label, width=10, height=2,
                    command=lambda c=cmd: send_cmd(c))
    btn.grid(row=0, column=i, padx=5)

# === GUI UPDATE LOGIC ===
last_data_time = time.time()   # Tracks last time we got data from Pi
byte_counter = 0               # Tracks bytes received per second
last_rate_time = time.time()   # Tracks last time we updated transfer rate

# ------------------------------------------------------------------------------------------------------#

def update_gui():
    """Main loop to read from Pi, update labels, and show health."""
    global last_data_time, byte_counter, last_rate_time

    try:
        # Try to read data from the Pi (non-blocking)
        data = sock.recv(1024).decode('utf-8')
        byte_counter += len(data.encode('utf-8'))  # Count raw bytes

        # Strip ANSI escape codes like \033[2A
        data = re.sub(r'\033\[[0-9;]*[A-Za-z]', '', data)

        # Extract status lines
        lines = data.strip().split('\n')
        if len(lines) >= 1:
            status_label.config(text=lines[0])         # First line = robot status
            last_data_time = time.time()               # Update last successful receive

    except BlockingIOError:
        pass  # Nothing to read this time, no error

    # Update connection health indicator
    if time.time() - last_data_time > 1.5:
        conn_label.config(text="❌ Disconnected", fg="red")
    else:
        conn_label.config(text="✅ Connected", fg="green")

    # Update transfer rate every second
    if time.time() - last_rate_time >= 1.0:
        rate_label.config(text=f"pi2mac speed: {byte_counter} B/s")
        byte_counter = 0
        last_rate_time = time.time()

    root.after(50, update_gui)  # Schedule this function to run again in 50ms

 # ------------------------------------------------------------------------------------------------------#   

# Start the periodic GUI update loop
update_gui()

# Start the GUI event loop
root.mainloop()