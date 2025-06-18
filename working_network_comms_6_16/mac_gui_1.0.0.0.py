import tkinter as tk
from modules.gui_modules import (
    setup_tcp_socket,
    setup_gui_window,
    create_status_labels,
    create_command_buttons,
    launch_video,
    close_video_stream,
    check_pi_response
)

# ---- INIT ----
ffplay_process = None
last_pi_data_json = [""]  # wrapped in list to be mutable in callback

# ---- SETUP ----
mac_socket = setup_tcp_socket()
mac_host = setup_gui_window()
status_vars = create_status_labels(mac_host)

# ---- BUTTONS ----
button_frame = tk.Frame(mac_host)
button_frame.pack(pady=10)

for b in create_command_buttons(button_frame, mac_socket, status_vars["sent_status"]):
    b.pack(side='left', padx=5)

video_button = tk.Button(mac_host, text="Launch Video Stream", command=lambda: launch_video_wrapper())
video_button.pack(pady=10)

stop_video_button = tk.Button(mac_host, text="Stop Video Stream", command=lambda: stop_video_wrapper())
stop_video_button.pack(pady=10)

exit_button = tk.Button(mac_host, text="Close GUI", command=lambda: exit_gui())
exit_button.pack(pady=10)

# ---- VIDEO STREAM CONTROL ----
def launch_video_wrapper():
    global ffplay_process
    if ffplay_process is None or ffplay_process.poll() is not None:
        ffplay_process = launch_video()  # ✅ this was missing before

def exit_gui():
    global ffplay_process
    print("[MAC] Closing GUI")
    close_video_stream(ffplay_process)
    mac_host.destroy()

def stop_video_wrapper():
    global ffplay_process
    if ffplay_process:
        close_video_stream(ffplay_process)
        ffplay_process = None


# ---- START LOOP ----
check_pi_response(mac_socket, status_vars, mac_host, last_pi_data_json)
mac_host.mainloop()