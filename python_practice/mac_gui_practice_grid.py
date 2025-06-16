import tkinter as tk
import socket
import select

last_pi_data = ""

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
    sent_status.set("Sent Z")
    print("Sending Z")

def b_button():
    mac_socket.sendall(b'b')
    sent_status.set("Sent B")
    print("Sending B")

def s_button():
    mac_socket.sendall(b's')
    sent_status.set("Sent S")
    print("Sending S")

def f_button():
    mac_socket.sendall(b'f')
    sent_status.set("Sent f")
    print("Sending F")

def r_button():
    mac_socket.sendall(b'r')
    sent_status.set("Sent r")
    print("Sending R")

def l_button():
    mac_socket.sendall(b'l')
    sent_status.set("Sent l")
    print("Sending L")


# Read data from socket
def check_pi_response():
    global last_pi_data

    read_socket, _, _= select.select([mac_socket], [], [], 1)
    if mac_socket in read_socket:
        pi_data = mac_socket.recv(1024).decode().strip().split('\n')[0]

        if pi_data != last_pi_data:
            rcv_status.set(f"Received {pi_data}")
            last_pi_data = pi_data
            print(f"[MAC] Received from Pi: {pi_data}")
    mac_host.after(100, check_pi_response)

# === TOP: Status labels ===
sent_status = tk.StringVar()
sent_label = tk.Label(mac_host, textvariable=sent_status)
sent_label.grid(row=2, column=2, pady=10)
sent_status.set("PI GUI Placedholder")

rcv_status = tk.StringVar()
rcv_label = tk.Label(mac_host, textvariable=rcv_status)
rcv_label.grid(row=1, column=2,pady=10)
rcv_status.set("Waiting for pi")

button1 = tk.Button(mac_host, text="z button", command=z_button)
button2 = tk.Button(mac_host, text="b button", command=b_button)
button3 = tk.Button(mac_host, text="s button", command=s_button)
button4 = tk.Button(mac_host, text="f button", command=f_button)
button5 = tk.Button(mac_host, text="r button", command=r_button)
button6 = tk.Button(mac_host, text="l button", command=l_button)

button1.grid(row=3, column=1, padx=5)
button2.grid(row=3, column=2, padx=5)
button3.grid(row=3, column=3, padx=5)
button4.grid(row=3, column=4, padx=5)
button5.grid(row=3, column=5, padx=5)
button6.grid(row=3, column=6, padx=5)

# Step 4: Start the GUI
check_pi_response()
mac_host.mainloop()