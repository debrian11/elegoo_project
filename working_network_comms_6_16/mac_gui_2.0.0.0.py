import tkinter as tk
import socket
import select
import json
import subprocess
# This will have the mac gui sending a json mssg to the pi for commands of each side of the motors

last_pi_data_json = ""
ffplay_process = None

# ------------------------  TCP SETUP ------------------------ #
PI_IP = "192.168.0.63"
PORT = 9000
mac_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mac_socket.connect((PI_IP, PORT))
mac_socket.setblocking(False)
print(f"[MAC] Connected to Pi at {PI_IP} and port {PORT}")


# Read JSON data from socket
def check_pi_response():
    global last_pi_data_json

    read_socket, _, _= select.select([mac_socket], [], [], 1)
    if mac_socket in read_socket:
        pi_data_json = mac_socket.recv(1024).decode().strip().split('\n')[0]
        rcv_status.set("Pi Status: Connected")

        #{ "L_motor":left_motor_speed, "R_motor":right_motor_speed, "distance":0, "time":current_time}
        if pi_data_json != last_pi_data_json:
            try:
                read_json_data = json.loads(pi_data_json)
                servo_status.set(f"Servo: {read_json_data.get('servo', 'N/A')}")
                motor_status.set(f"Motor: {read_json_data.get('motor', 'N/A')}")
                distance_status.set(f"Distance: {read_json_data.get('distance', 'N/A')}")
                time_status.set(f"Time: {read_json_data.get('time', 'N/A')}")
                raw_json_rcvd_status.set(f"Raw Arduino JSON: {pi_data_json}")

            except (json.JSONDecodeError, ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                rcv_status.set(f"Pi Status: Disconnected")
                print(f"[MAC ERROR] Failed to parse: {pi_data_json}")

            last_pi_data_json = read_json_data

    mac_host.after(100, check_pi_response)

# ------------------------  GUI SETUP ------------------------ #
mac_host = tk.Tk()
mac_host.update_idletasks()  # force geometry info to update
mac_host.title("Test GUI")

window_width = 800
window_height = 500
screen_width = mac_host.winfo_screenwidth()
screen_height = mac_host.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
mac_host.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")


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

time_status = tk.StringVar()
time_label = tk.Label(mac_host, textvariable=time_status)
time_label.pack()

# === BOTTOM: Button row container ===
button_frame = tk.Frame(mac_host)
button_frame.pack(pady=10)

# LEFT column — motor buttons
left_frame = tk.Frame(button_frame)
left_frame.pack(side='left', padx=20)

# MIDDLE column — slider
mid_frame = tk.Frame(button_frame)
mid_frame.pack(side='left', padx=20)

# RIGHT column — video + exit
right_frame = tk.Frame(button_frame)
right_frame.pack(side='left', padx=20)


def b_button():
    mac_json_msg = build_motor_json(0.5, 0.5, 0, 0) # ( L_PWM %, R_PWM %, L_motor DIR, R_motor DIR)
    mac_socket.sendall((mac_json_msg + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status:  fwd | Raw = {mac_json_msg}")
    print(f"Sending {mac_json_msg}")

def f_button():
    mac_json_msg = build_motor_json(1.0, 1.0, 1, 1)
    mac_socket.sendall((mac_json_msg + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status:  fwd | Raw = {mac_json_msg}")
    print(f"Sending {mac_json_msg}")

def r_button():
    mac_json_msg = build_motor_json(0.5, 0.1, 1, 1)
    mac_socket.sendall((mac_json_msg + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status:  fwd | Raw = {mac_json_msg}")
    print(f"Sending {mac_json_msg}")

def l_button():
    mac_json_msg = build_motor_json(0.1, 0.5, 1, 1)
    mac_socket.sendall((mac_json_msg + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status:  fwd | Raw = {mac_json_msg}")
    print(f"Sending {mac_json_msg}")

def s_button():
    mac_json_msg = build_motor_json(0.0, 0.0, 1, 1)
    mac_socket.sendall((mac_json_msg + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status:  fwd | Raw = {mac_json_msg}")
    print(f"Sending {mac_json_msg}")

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
        ffplay_process = launch_video()

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

# ------------------------  MOTOR INPUT ------------------------ #
user_pwm=tk.StringVar()
pwm_1=user_pwm.get()

def user_input_pwm():    
    print("PWM % Value : " + pwm_1)
    user_pwm.set("")
    
pwm_label = tk.Label(mid_frame, text='PWM % (0 --> 100%)', font=('calibre',10, 'bold'))
pwm_entry = tk.Entry(mid_frame,textvariable = user_pwm, font=('calibre',10,'normal'))

# placing the label and entry in
pwm_label.pack(pady=2)
pwm_entry.pack(pady=2)

def get_pwm_from_entry():
    try:
        percent = float(user_pwm.get())
        return max(50, min(150, int(50 + (percent / 100) * 100)))
    except ValueError:
        return 50  # fallback PWM if invalid input

def build_motor_json(left_mult, right_mult, left_dir, right_dir):
    base_pwm = get_pwm_from_entry()
    return json.dumps({
        "L_DIR": left_dir,
        "R_DIR": right_dir,
        "L_PWM": int(base_pwm * left_mult),
        "R_PWM": int(base_pwm * right_mult)
    })

# ------------------------  BUTTONS ------------------------ #
button2 = tk.Button(left_frame, text="Back", command=b_button)
button3 = tk.Button(left_frame, text="Stop", command=s_button)
button4 = tk.Button(left_frame, text="Forward", command=f_button)
button5 = tk.Button(left_frame, text="Right", command=r_button)
button6 = tk.Button(left_frame, text="Left", command=l_button)
video_button = tk.Button(right_frame, text="Launch Video Stream", command=launch_video_wrapper)
stop_video_button = tk.Button(right_frame, text="Stop Video Stream", command=stop_video_wrapper)
exit_button = tk.Button(right_frame, text="Close GUI", command=exit_gui)

button2.pack(pady=2)
button3.pack(pady=2)
button4.pack(pady=2)
button5.pack(pady=2)
button6.pack(pady=2)
video_button.pack(pady=5)
stop_video_button.pack(pady=5)
exit_button.pack(pady=5)

# ------------------------  START GUI ------------------------ #
check_pi_response()
mac_host.mainloop()