import tkinter as tk
import socket
import select
import json
import subprocess
# This will have the mac gui sending a json mssg to the pi for commands of each side of the motors
# 6/29/2025
# add servo angle to display
# Add 2nd gui for the nano encoder for future plotting
# add nano json reading
# add json parsing of elegoo vs nano
# 7/10/2025
# removed servo references having the 3 USS from the nano
# 8/3/2025
# Add arrow key buttons to hold

last_pi_data_json = ""
ffplay_process = None

# Store default values for motor
last_left_mult = 0.0
last_right_mult = 0.0
last_left_dir = 1
last_right_dir = 1

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

    read_socket, _, _ = select.select([mac_socket], [], [], 1)
    if mac_socket in read_socket:
        try:
            pi_data_json = mac_socket.recv(1024).decode().strip().split('\n')[0]

            if pi_data_json and pi_data_json != last_pi_data_json:
                try:
                    read_json_data = json.loads(pi_data_json)
                    source = read_json_data.get("source", "UNKNOWN")
                    if source == "ELEGOO":
                        # {"mssg_id":106,"L_motor":0,"R_motor":0}
                        elegoo_mssg_id.set(f"Messge ID: {read_json_data.get('mssg_id', 'N/A')}")
                        left_motor_pwm.set(f"Left Motor PWM: {read_json_data.get('L_motor', 'N/A')}")
                        right_motor_pwm.set(f"Right Motor PWM: {read_json_data.get('R_motor', 'N/A')}")
                        elegoo_raw_json_rcvd_status.set(f"Raw Arduino JSON: {pi_data_json}")

                    elif source == "NANO":
                        # {"mssg_id":993,"F_USS":12,"L_USS":16,"R_USS":89,"L_ENCD":315,"R_ENCD":52}
                        nano_mssg_id.set(f"Messge ID: {read_json_data.get('mssg_id', 'N/A')}")
                        heading_status.set(f"Heading: {read_json_data.get('HEAD', 'N/A')}")
                        left_motor_encoder.set(f"Left Encoder: {read_json_data.get('L_ENCD', 'N/A')}")
                        right_motor_encoder.set(f"Right Encoder: {read_json_data.get('R_ENCD', 'N/A')}")
                        f_dist_status.set(f"Front USS: {read_json_data.get('F_USS', 'N/A')}")
                        l_dist_status.set(f"Left USS: {read_json_data.get('L_USS', 'N/A')}")
                        r_dist_status.set(f"Right USS: {read_json_data.get('R_USS', 'N/A')}")
                        nano_raw_json_rcvd_status.set(f"Raw Arduino JSON: {pi_data_json}")

                    last_pi_data_json = pi_data_json

                except json.JSONDecodeError:
                    print(f"[MAC ERROR] Bad JSON: {pi_data_json}")

        except Exception as e:
            print(f"[MAC ERROR] Socket error: {e}")

    control_gui.after(100, check_pi_response)

# ------------------------  GUI SETUP ------------------------ #
# First GUI for motor control
control_gui = tk.Tk()
control_gui.update_idletasks()  # force geometry info to update
control_gui.title("Control GUI")

gui1_window_width = 1000
gui1_window_height = 700
screen_width = control_gui.winfo_screenwidth()
screen_height = control_gui.winfo_screenheight()
center_x = int(screen_width / 2 - gui1_window_width / 2)
center_y = int(screen_height / 2 - gui1_window_height / 2)
control_gui.geometry(f"{gui1_window_width}x{gui1_window_height}+{center_x}+{center_y}")

control_gui_title_label = tk.Label(
    control_gui,
    text="Elegoo Motor Telemetry",
    font=("Helvetica", 20, "bold"),
    bg="white",
    fg="black"
)
control_gui_title_label.pack(pady=20)

# 2nd GUI for plotting
# ------------- Plotting GUI Setup (Fixed) -------------
plot_gui = tk.Toplevel(control_gui)
plot_gui.title("Plot GUI")

gui2_window_width = 800
gui2_window_height = 500
plot_gui.geometry(f"{gui2_window_width}x{gui2_window_height}")

# Optional: Add a title label for clarity
plot_gui_title_label = tk.Label(
    plot_gui,
    text="NANO Encoder Telemetry",
    font=("Helvetica", 20, "bold"),
    bg="white",
    fg="black"
)
plot_gui_title_label.pack(pady=20)

# Left Encoder Label
left_motor_encoder = tk.StringVar()
left_motor_encoder_label = tk.Label(plot_gui, textvariable=left_motor_encoder)
left_motor_encoder_label.pack(pady=10)
left_motor_encoder.set("Left Encoder: ---")  # <- This forces text to appear at launch

# Right Encoder Label
right_motor_encoder = tk.StringVar()
right_motor_encoder_label = tk.Label(plot_gui, textvariable=right_motor_encoder)
right_motor_encoder_label.pack(pady=10)
right_motor_encoder.set("Right Encoder: ---")  # <- Forces label to appear at launch

# Heading Label
heading_status = tk.StringVar()
heading_status_label = tk.Label(plot_gui, textvariable=heading_status)
heading_status_label.pack(pady=10)
heading_status.set("Heading: ---")  # <- Forces label to appear at launch

nano_time_status = tk.StringVar()
nano_time_label = tk.Label(plot_gui, textvariable=nano_time_status)
nano_time_label.pack()

nano_mssg_id = tk.StringVar()
nano_mssg_id_label = tk.Label(plot_gui, textvariable=nano_mssg_id)
nano_mssg_id_label.pack()

elegoo_mssg_id = tk.StringVar()
elegoo_mssg_id_label = tk.Label(control_gui, textvariable=elegoo_mssg_id)
elegoo_mssg_id_label.pack()

# === Control GUI : Status labels ===

# Mac send Status
mac_sent_status = tk.StringVar()
mac_sent_label = tk.Label(control_gui, textvariable=mac_sent_status)
mac_sent_label.pack(pady=5)
mac_sent_status.set("Mac Mac Send Status: ")

# Elegoo Arduino message received
elegoo_raw_json_rcvd_status = tk.StringVar()
elegoo_raw_json_rcvd_status_label = tk.Label(control_gui, textvariable=elegoo_raw_json_rcvd_status)
elegoo_raw_json_rcvd_status_label.pack(pady=5)
elegoo_raw_json_rcvd_status.set("Raw Arduino Recvd Data: ")

# Nano Arduino message received
nano_raw_json_rcvd_status = tk.StringVar()
nano_raw_json_rcvd_status_label = tk.Label(plot_gui, textvariable=nano_raw_json_rcvd_status)
nano_raw_json_rcvd_status_label.pack(pady=5)
nano_raw_json_rcvd_status.set("Raw Arduino Recvd Data: ")

# Motor PWM speeds
left_motor_pwm = tk.StringVar()
left_motor_pwm_label = tk.Label(control_gui, textvariable=left_motor_pwm)
left_motor_pwm_label.pack()

right_motor_pwm = tk.StringVar()
right_motor_pwm_label = tk.Label(control_gui, textvariable=right_motor_pwm)
right_motor_pwm_label.pack()

# Ultrasonic Stuff
f_dist_status = tk.StringVar()
f_dist_label = tk.Label(plot_gui, textvariable=f_dist_status)
f_dist_label.pack()

l_dist_status = tk.StringVar()
l_dist_label = tk.Label(plot_gui, textvariable=l_dist_status)
l_dist_label.pack()

r_dist_status = tk.StringVar()
r_dist_label = tk.Label(plot_gui, textvariable=r_dist_status)
r_dist_label.pack()


elegoo_time_status = tk.StringVar()
elegoo_time_label = tk.Label(control_gui, textvariable=elegoo_time_status)
elegoo_time_label.pack()

# === BOTTOM: Button row container ===
button_frame = tk.Frame(control_gui)
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

arrow_frame = tk.Frame(control_gui)
arrow_frame.pack(pady=10)
# Arrow Buttons (Hold to Move)
arrow_up = tk.Button(arrow_frame, text="↑", width=5, height=2)
arrow_up.grid(row=0, column=1, padx=5, pady=5)
arrow_up.bind("<ButtonPress-1>", lambda e: f_button())
arrow_up.bind("<ButtonRelease-1>", lambda e: s_button())

arrow_left = tk.Button(arrow_frame, text="←", width=5, height=2)
arrow_left.grid(row=1, column=0, padx=5, pady=5)
arrow_left.bind("<ButtonPress-1>", lambda e: l_button())
arrow_left.bind("<ButtonRelease-1>", lambda e: s_button())

arrow_down = tk.Button(arrow_frame, text="↓", width=5, height=2)
arrow_down.grid(row=1, column=1, padx=5, pady=5)
arrow_down.bind("<ButtonPress-1>", lambda e: b_button())
arrow_down.bind("<ButtonRelease-1>", lambda e: s_button())

arrow_right = tk.Button(arrow_frame, text="→", width=5, height=2)
arrow_right.grid(row=1, column=2, padx=5, pady=5)
arrow_right.bind("<ButtonPress-1>", lambda e: r_button())
arrow_right.bind("<ButtonRelease-1>", lambda e: s_button())



# ============= DEFINE MOTOR BUTTONS ================ 
def b_button(): # Back
    global last_left_mult, last_right_mult, last_left_dir, last_right_dir
    last_left_mult = 0.75
    last_right_mult = 0.64
    last_left_dir = 0
    last_right_dir = 0

    mac_json_msg = build_motor_json(last_left_mult, last_right_mult, last_left_dir, last_right_dir)
    mac_socket.sendall((mac_json_msg + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status: back | Raw = {mac_json_msg}")
    print(f"Sending {mac_json_msg}")

def f_button(): # Forward
    global last_left_mult, last_right_mult, last_left_dir, last_right_dir
    last_left_mult = 1.0
    last_right_mult = 0.73
    last_left_dir = 1
    last_right_dir = 1

    mac_json_msg = build_motor_json(last_left_mult, last_right_mult, last_left_dir, last_right_dir)
    mac_socket.sendall((mac_json_msg + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status:  fwd | Raw = {mac_json_msg}")
    print(f"Sending {mac_json_msg}")

def r_button(): # Right
    global last_left_mult, last_right_mult, last_left_dir, last_right_dir
    last_left_mult = 0.8
    last_right_mult = 0.0
    last_left_dir = 1
    last_right_dir = 1

    mac_json_msg = build_motor_json(last_left_mult, last_right_mult, last_left_dir, last_right_dir)
    mac_socket.sendall((mac_json_msg + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status: right | Raw = {mac_json_msg}")
    print(f"Sending {mac_json_msg}")

def l_button(): # Left
    global last_left_mult, last_right_mult, last_left_dir, last_right_dir
    last_left_mult = 0.0
    last_right_mult = 1.0
    last_left_dir = 1
    last_right_dir = 1

    mac_json_msg = build_motor_json(last_left_mult, last_right_mult, last_left_dir, last_right_dir)
    mac_socket.sendall((mac_json_msg + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status: left | Raw = {mac_json_msg}")
    print(f"Sending {mac_json_msg}")

def s_button(): # Stop
    global last_left_mult, last_right_mult, last_left_dir, last_right_dir
    last_left_mult = 0.0
    last_right_mult = 0.0
    last_left_dir = 1
    last_right_dir = 1

    mac_json_msg = build_motor_json(last_left_mult, last_right_mult, last_left_dir, last_right_dir)
    mac_socket.sendall((mac_json_msg + '\n').encode('utf-8'))   
    mac_sent_status.set(f"Mac Send Status: stop | Raw = {mac_json_msg}")
    print(f"Sending {mac_json_msg}")


# ============ Arrow buttons


# ============= DEFINE OTHER BUTTONS ================ 
def exit_gui():
    print("[MAC] Closing GUI")
    close_video_stream(ffplay_process)
    control_gui.destroy()
    plot_gui.destroy()

def launch_video():
    return subprocess.Popen([
        "ffplay", "-fflags", "nobuffer", "-flags", "low_delay", "-framedrop", "udp://@:1235"
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

def send_motor_command():
    json_cmd = build_motor_json(last_left_mult, last_right_mult, last_left_dir, last_right_dir)
    mac_socket.sendall((json_cmd + '\n').encode('utf-8'))
    mac_sent_status.set(f"Mac Send Status: Sweep | Raw = {json_cmd}")
    print("[MAC GUI] Sent motor JSON:", json_cmd)

# ------------------------  MOTOR INPUT ------------------------ #
user_pwm=tk.StringVar()
    
pwm_label = tk.Label(mid_frame, text='PWM % (0 --> 100%)', font=('calibre',10, 'bold'))
pwm_entry = tk.Entry(mid_frame,textvariable = user_pwm, font=('calibre', 10, 'normal'))
pwm_label.pack(pady=2)
pwm_entry.pack(pady=2)

def get_pwm_from_entry():
    min_motor_pwm = 85
    max_motor_pwm = 150
    try:
        percent = float(user_pwm.get())
        return max(min_motor_pwm, min(max_motor_pwm, int(min_motor_pwm + (percent / 100) * 100)))
    except ValueError:
        return min_motor_pwm  # fallback PWM if invalid input

def build_motor_json(left_mult, right_mult, left_dir, right_dir): # This returns a json string
    base_pwm = get_pwm_from_entry()
    return json.dumps({
        "L_DIR": left_dir,
        "R_DIR": right_dir,
        "L_PWM": int(base_pwm * left_mult),
        "R_PWM": int(base_pwm * right_mult),
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
tk.mainloop()
