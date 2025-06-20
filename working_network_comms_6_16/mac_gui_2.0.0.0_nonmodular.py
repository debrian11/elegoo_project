import tkinter as tk
import socket
import select
import json
import subprocess
# This will have the mac gui sending a json mssg to the pi for commands of each side of the motors

last_pi_data_json = ""
ffplay_process = None
#last_pi_data_json = [""]  # wrapped in list to be mutable in callback

# TCP Socket setup
PI_IP = "192.168.0.63"
PORT = 9000
mac_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mac_socket.connect((PI_IP, PORT))
mac_socket.setblocking(False)
print(f"[MAC] Connected to Pi at {PI_IP} and port {PORT}")

fwd_json = '{ "L_motor":"100", "R_motor":"100" }'
bwd_json = '{ "L_motor":"75", "R_motor":"75" }'
right_json = '{ "L_motor":"50", "R_motor":"100" }'
left_json = '{ "L_motor":"100", "R_motor":"50" }'
stop_json = '{ "L_motor":"0", "R_motor":"0" }'


# GUI SETUP
mac_host = tk.Tk()
mac_host.title("Test GUI")
mac_host.geometry("800x500+200+100") # width x height

# Button stuff to send characters
#def z_button():
#    #mac_socket.sendall(b'z')
#    mac_socket.sendall(f'{fwd_json}')
#    mac_sent_status.set("Mac Send Status:  fwd")
#    print(f"Sending {fwd_json}")

def b_button():
    #mac_socket.sendall(b'b')
    mac_socket.sendall((f'{bwd_json}' + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status:  bwd | Raw output = {bwd_json})")
    print(f"Sending {bwd_json}")

def s_button():
    #mac_socket.sendall(b's')
    mac_socket.sendall((f'{stop_json}' + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status:  stop | Raw output = {stop_json})")
    print(f"Sending {stop_json}")

def f_button():
    #mac_socket.sendall(b'z')
    mac_socket.sendall((f'{fwd_json}' + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status:  fwd | Raw output = {fwd_json})")
    print(f"Sending {fwd_json}")

def r_button():
    mac_socket.sendall((f'{right_json}' + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status:  right | Raw output = {right_json})")
    print(f"Sending {right_json}")

def l_button():
    mac_socket.sendall((f'{left_json}' + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status:  left | Raw output = {left_json})")
    print(f"Sending {left_json}")


def exit_gui():
    global ffplay_process
    print("[MAC] Closing GUI")
    close_video_stream(ffplay_process)
    mac_host.destroy()

def launch_video():
    return subprocess.Popen([
        "ffplay",
        "-fflags", "nobuffer",
        "-flags", "low_delay",
        "-framedrop",
        "udp://@:1235"
    ])

def launch_video_wrapper():
    global ffplay_process
    if ffplay_process is None or ffplay_process.poll() is not None:
        ffplay_process = launch_video()  # ✅ this was missing before

def close_video_stream(process):
    if process and process.poll() is None:
        process.terminate()
        process.wait()
        print("[MAC] ffplay process closed.")

def stop_video_wrapper():
    global ffplay_process
    if ffplay_process:
        close_video_stream(ffplay_process)
        ffplay_process = None


# Read JSON data from socket
def check_pi_response():
    global last_pi_data_json

    read_socket, _, _= select.select([mac_socket], [], [], 1)
    if mac_socket in read_socket:
        pi_data_json = mac_socket.recv(1024).decode().strip().split('\n')[0]
        rcv_status.set("Pi Status: Connected")

        if pi_data_json != last_pi_data_json:
            try:
                read_json_data = json.loads(pi_data_json)
                servo_status.set(f"Servo: {read_json_data.get('servo', 'N/A')}")
                motor_status.set(f"Motor: {read_json_data.get('motor', 'N/A')}")
                distance_status.set(f"Distance: {read_json_data.get('distance', 'N/A')}")
                raw_json_rcvd_status.set(f"Raw Arduino JSON: {pi_data_json}")
            except json.JSONDecodeError:
                rcv_status.set(f"[BAD JSON] {read_json_data}")
                print(f"[MAC ERROR] Failed to parse: {read_json_data}")

            last_pi_data_json = read_json_data

    mac_host.after(100, check_pi_response)

# === TOP: Status labels ===
rcv_status = tk.StringVar()
rcv_label = tk.Label(mac_host, textvariable=rcv_status)
rcv_label.pack(pady=10)
rcv_status.set("Pi Status: ")

mac_sent_status = tk.StringVar()
mac_sent_label = tk.Label(mac_host, textvariable=mac_sent_status)
mac_sent_label.pack(pady=5)
mac_sent_status.set("Mac Mac Send Status: ")

raw_json_rcvd_status = tk.StringVar()
raw_json_rcvd_status_label = tk.Label(mac_host, textvariable=raw_json_rcvd_status)
raw_json_rcvd_status_label.pack(pady=5)
raw_json_rcvd_status.set("Raw Arduino Recvd Data: ")

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
#button1 = tk.Button(button_frame, text="z button", command=z_button)
button2 = tk.Button(button_frame, text="b button", command=b_button)
button3 = tk.Button(button_frame, text="s button", command=s_button)
button4 = tk.Button(button_frame, text="f button", command=f_button)
button5 = tk.Button(button_frame, text="r button", command=r_button)
button6 = tk.Button(button_frame, text="l button", command=l_button)
video_button = tk.Button(mac_host, text="Launch Video Stream", command=lambda: launch_video_wrapper())
stop_video_button = tk.Button(mac_host, text="Stop Video Stream", command=lambda: stop_video_wrapper())
exit_button = tk.Button(mac_host, text="Close GUI", command=lambda: exit_gui())


#button1.pack(side='left', padx=5)
button2.pack(side='left', padx=5)
button3.pack(side='left', padx=5)
button4.pack(side='left', padx=5)
button5.pack(side='left', padx=5)
button6.pack(side='left', padx=5)
video_button.pack(pady=10)
stop_video_button.pack(pady=10)
exit_button.pack(pady=10)

# Step 4: Start the GUI
check_pi_response()
mac_host.mainloop()