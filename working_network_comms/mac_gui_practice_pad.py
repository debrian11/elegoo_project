import tkinter as tk
import socket
import select
import json
last_pi_data_json = ""

# TCP Socket setup
PI_IP = "192.168.0.63"
PORT = 9000
mac_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mac_socket.connect((PI_IP, PORT))
mac_socket.setblocking(False)
print(f"[MAC] Connected to Pi at {PI_IP} and port {PORT}")


# GUI SETUP
mac_host = tk.Tk()
mac_host.title("Test GUI")
mac_host.geometry("800x500") # width x height

# Button stuff to send characters
def z_button():
    mac_socket.sendall(b'z')
    sent_status.set("Send Status:  Z")
    print("Sending Z")

def b_button():
    mac_socket.sendall(b'b')
    sent_status.set("Send Status:  B")
    print("Sending B")

def s_button():
    mac_socket.sendall(b's')
    sent_status.set("Send Status:  S")
    print("Sending S")

def f_button():
    mac_socket.sendall(b'f')
    sent_status.set("Send Status:  f")
    print("Sending F")

def r_button():
    mac_socket.sendall(b'r')
    sent_status.set("Send Status:  r")
    print("Sending R")

def l_button():
    mac_socket.sendall(b'l')
    sent_status.set("Send Status: L")
    print("Sending L")


# Read data from socket
def check_pi_response():
    global last_pi_data_json

    read_socket, _, _= select.select([mac_socket], [], [], 1)
    if mac_socket in read_socket:
        pi_data_json = mac_socket.recv(1024).decode().strip().split('\n')[0]
        rcv_status.set("Pi Status: Connected")

        if pi_data_json != last_pi_data_json:
            #rcv_status.set(f"Received {pi_data}")
            #last_pi_data = pi_data
            #print(f"[MAC] Received from Pi: {pi_data}")
            try:
                read_json_data = json.loads(pi_data_json)
                servo_status.set(f"Servo: {read_json_data.get('servo', 'N/A')}")
                motor_status.set(f"Motor: {read_json_data.get('motor', 'N/A')}")
                distance_status.set(f"Distance: {read_json_data.get('distance', 'N/A')}")
            except json.JSONDecodeError:
                rcv_status.set(f"[BAD JSON] {read_json_data}")
                print(f"[MAC ERROR] Failed to parse: {read_json_data}")

            last_pi_data_json = read_json_data

    mac_host.after(100, check_pi_response)

# === TOP: Status labels ===
rcv_status = tk.StringVar()
rcv_label = tk.Label(mac_host, textvariable=rcv_status)
rcv_label.pack(pady=10)
rcv_status.set("Pi Status")

sent_status = tk.StringVar()
sent_label = tk.Label(mac_host, textvariable=sent_status)
sent_label.pack(pady=5)
sent_status.set("Send Status: ")

servo_status = tk.StringVar()
servo_label = tk.Label(mac_host, textvariable=servo_status)
servo_label.pack()

motor_status = tk.StringVar()
motor_label = tk.Label(mac_host, textvariable=motor_status)
motor_label.pack()

distance_status = tk.StringVar()
distance_label = tk.Label(mac_host, textvariable=distance_status)
distance_label.pack()


# === BOTTOM: Button row container ===
button_frame = tk.Frame(mac_host)
button_frame.pack(pady=10)

# Add all buttons side-by-side in button_frame
button1 = tk.Button(button_frame, text="z button", command=z_button)
button2 = tk.Button(button_frame, text="b button", command=b_button)
button3 = tk.Button(button_frame, text="s button", command=s_button)
button4 = tk.Button(button_frame, text="f button", command=f_button)
button5 = tk.Button(button_frame, text="r button", command=r_button)
button6 = tk.Button(button_frame, text="l button", command=l_button)

button1.pack(side='left', padx=5)
button2.pack(side='left', padx=5)
button3.pack(side='left', padx=5)
button4.pack(side='left', padx=5)
button5.pack(side='left', padx=5)
button6.pack(side='left', padx=5)

# Step 4: Start the GUI
check_pi_response()
mac_host.mainloop()