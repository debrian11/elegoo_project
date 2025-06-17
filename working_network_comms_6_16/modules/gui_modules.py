import tkinter as tk
import socket
import subprocess
import json

# ---- TCP SETUP ----
def setup_tcp_socket(ip="192.168.0.63", port=9000):
    mac_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mac_socket.connect((ip, port))
    mac_socket.setblocking(False)
    print(f"[MAC] Connected to Pi at {ip} and port {port}")
    return mac_socket

# ---- GUI WINDOW SETUP ----
def setup_gui_window(title="Test GUI", width=800, height=500, x=200, y=100):
    mac_host = tk.Tk()
    mac_host.title(title)
    mac_host.update_idletasks()
    mac_host.geometry(f"{width}x{height}+{x}+{y}")
    return mac_host

# ---- STATUS LABELS ----
def create_status_labels(parent):
    rcv_status = tk.StringVar(value="Pi Status")
    sent_status = tk.StringVar(value="Send Status: ")
    servo_status = tk.StringVar()
    motor_status = tk.StringVar()
    distance_status = tk.StringVar()

    for var in [rcv_status, sent_status, servo_status, motor_status, distance_status]:
        tk.Label(parent, textvariable=var).pack(pady=5)

    return {
        "rcv_status": rcv_status,
        "sent_status": sent_status,
        "servo_status": servo_status,
        "motor_status": motor_status,
        "distance_status": distance_status
    }

# ---- BUTTON CREATION ----
def create_command_buttons(frame, sock, sent_status):
    def make_btn(label, byte):
        return tk.Button(frame, text=label, command=lambda: send_cmd(sock, sent_status, byte, label))

    return [
        make_btn("z button", b'z'),
        make_btn("b button", b'b'),
        make_btn("s button", b's'),
        make_btn("f button", b'f'),
        make_btn("r button", b'r'),
        make_btn("l button", b'l')
    ]

def send_cmd(sock, status_var, byte_cmd, label):
    sock.sendall(byte_cmd)
    status_var.set(f"Send Status: {label[-1].upper()}")
    print(f"Sending {label}")

# ---- VIDEO STREAM HANDLING ----
def launch_video():
    return subprocess.Popen([
        "ffplay",
        "-fflags", "nobuffer",
        "-flags", "low_delay",
        "-framedrop",
        "udp://@:1235"
    ])

def close_video_stream(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        proc.wait()
        print("[MAC] ffplay process closed.")

# ---- CHECK PI RESPONSE ----
def check_pi_response(sock, status_vars, root, last_data_ref):
    import select

    read_socket, _, _ = select.select([sock], [], [], 1)

    if sock in read_socket:
        pi_data_json = sock.recv(1024).decode().strip().split('\n')[0]
        status_vars["rcv_status"].set("Pi Status: Connected")

        if pi_data_json != last_data_ref[0]:
            try:
                data = json.loads(pi_data_json)
                status_vars["servo_status"].set(f"Servo: {data.get('servo', 'N/A')}")
                status_vars["motor_status"].set(f"Motor: {data.get('motor', 'N/A')}")
                status_vars["distance_status"].set(f"Distance: {data.get('distance', 'N/A')}")
                last_data_ref[0] = pi_data_json
            except json.JSONDecodeError:
                status_vars["rcv_status"].set(f"[BAD JSON] {pi_data_json}")
                print(f"[MAC ERROR] Failed to parse: {pi_data_json}")

    root.after(100, lambda: check_pi_response(sock, status_vars, root, last_data_ref))