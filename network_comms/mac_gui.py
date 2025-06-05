import tkinter as tk
import socket
import re
import time

# === CONFIG ===
PI_IP = "192.168.0.63"  # <-- Replace with your Pi's IP
PORT = 9000

# === TCP Client Setup ===
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PI_IP, PORT))
sock.setblocking(False)

# === GUI Setup ===
root = tk.Tk()
root.title("Robot Status Dashboard")
root.geometry("600x280")

# === Status Labels ===
status_label = tk.Label(root, text="Status: ...", font=("Courier", 16), anchor="w", justify="left")
status_label.pack(padx=10, pady=(20, 5), anchor="w")

conn_label = tk.Label(root, text="Connection: ✅ Connected", font=("Courier", 14), anchor="w", justify="left", fg="green")
conn_label.pack(padx=10, pady=(0, 5), anchor="w")

rate_label = tk.Label(root, text="Transfer: -- B/s", font=("Courier", 12), anchor="w", justify="left")
rate_label.pack(padx=10, pady=(0, 5), anchor="w")

# === Send Command Function ===
def send_cmd(cmd):
    try:
        sock.sendall((cmd + '\n').encode('utf-8'))
    except Exception as e:
        print(f"Send failed: {e}")

# === Command Buttons ===
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

commands = ['f', 'b', 'l', 'r', 's', 'z']
labels = ['Forward', 'Backward', 'Left', 'Right', 'Stop', 'Sweep']

for i, (cmd, label) in enumerate(zip(commands, labels)):
    btn = tk.Button(button_frame, text=label, width=10, height=2,
                    command=lambda c=cmd: send_cmd(c))
    btn.grid(row=0, column=i, padx=5)

# === Live Status Update ===
last_data_time = time.time()
byte_counter = 0
last_rate_time = time.time()

def update_gui():
    global last_data_time, byte_counter, last_rate_time

    try:
        data = sock.recv(1024).decode('utf-8')
        byte_counter += len(data.encode('utf-8'))  # raw bytes received

        data = re.sub(r'\033\[[0-9;]*[A-Za-z]', '', data)
        lines = data.strip().split('\n')
        if len(lines) >= 1:
            status_label.config(text=lines[0])
            last_data_time = time.time()

    except BlockingIOError:
        pass

    # Connection health indicator
    if time.time() - last_data_time > 1.5:
        conn_label.config(text="❌ Disconnected", fg="red")
    else:
        conn_label.config(text="✅ Connected", fg="green")

    # Transfer rate display (B/s)
    if time.time() - last_rate_time >= 1.0:
        rate_label.config(text=f"pi2mac speed: {byte_counter} B/s")
        byte_counter = 0
        last_rate_time = time.time()

    root.after(50, update_gui)

update_gui()
root.mainloop()
