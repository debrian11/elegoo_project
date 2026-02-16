#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304. C0411, E0401
# Python Script for GUI
import json
import os
import csv
import socket
import select
import sys
import time
import subprocess
import argparse
import m_data_mgr_module as dmm
import m_yaml_data as yd

from PyQt5.QtCore import QTimer, QProcess
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QVBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QWidget, QMainWindow)

# Arge parser
the_parser = argparse.ArgumentParser(
    description='Sets IP setting to either local or to pi'
)

the_parser.add_argument('-i', '--ip', type=int, default=0)  # 0 = Local | 1 = Pi
the_parser.add_argument('-c', '--csv', type=int, default=0) # 0 = disabled | 1 = enabled
args = the_parser.parse_args()
ip_setting = args.ip
csv_logging_enabled = args.csv

class CmdGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Parse out the yml to grab the ports
        self.yaml_file_name = 'pi_config.yml'
        self.parsed_out_yml = dmm.parse_yaml(self.yaml_file_name)

        # Read Sockets
        self.read_tm_socket_list = yd.read_tm_sockets(self.parsed_out_yml, 0)
        self.tm_timer = QTimer(self)
        self.tm_timer.timeout.connect(self.read_tm) #read_tm = custom method
        self.tm_timer.start(50) # ms   

        # TX Sockets
        self.sendpoints = yd.send_ports(self.parsed_out_yml, ip_setting)
        self.vid_ip = self.sendpoints["vid_cmd"][0]
        self.vid_port = self.sendpoints["vid_cmd"][1]
        self.interval_list = yd.intervals_read_send(self.parsed_out_yml)
        self.pi1_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # --- Create UI Layout ---
        self.setWindowTitle("Pi Bot Command GUI")
        layout =        QHBoxLayout()
        layout_nano =   QVBoxLayout()
        layout_elegoo = QVBoxLayout()
        layout_btns =   QVBoxLayout()
        layout_vid_btns = QVBoxLayout()

        # Sent status
        self.cmd_sent = QLabel("CMD:  N/A")
        self.pwr_sent = QLabel("PWR:  N/A")
        layout_btns.addWidget(self.cmd_sent)
        layout_btns.addWidget(self.pwr_sent)

        # Nano TM Data
        self.uss_f_status   = QLabel("USS F:  N/A")
        self.uss_r_status   = QLabel("USS R:  N/A")
        self.uss_l_status   = QLabel("USS L:  N/A")
        self.head_status    = QLabel("HEAD:  N/A")
        self.l_encd_status  = QLabel("ENCD L:  N/A")
        self.r_encd_status  = QLabel("ENCD R:  N/A")
        self.nano_id_status = QLabel("NANO ID:  N/A")
        self.f_uss   = None
        self.r_uss   = None
        self.l_uss   = None
        self.head    = None
        self.l_encd  = None
        self.r_encd  = None
        self.nano_id = None


        # Elegoo TM Data
        self.l_motor_status     = QLabel("MOTOR L:  N/A")
        self.r_motor_status     = QLabel("MOTOR R:  N/A")
        self.elegoo_id_status   = QLabel("ELEGOO ID:  N/A")
        self.l_motor   = None
        self.r_motor   = None
        self.elegoo_id = None

        # Vid status
        self.vid_status = QLabel("Video Status:  N/A")

        # Add labels to the GUI; FUTURE = condense this section
        layout_nano.addWidget(self.uss_f_status)
        layout_nano.addWidget(self.uss_r_status)
        layout_nano.addWidget(self.uss_l_status)
        layout_nano.addWidget(self.head_status)
        layout_nano.addWidget(self.l_encd_status)
        layout_nano.addWidget(self.r_encd_status)
        layout_nano.addWidget(self.nano_id_status)

        layout_elegoo.addWidget(self.l_motor_status)
        layout_elegoo.addWidget(self.r_motor_status)
        layout_elegoo.addWidget(self.elegoo_id_status)

        layout_vid_btns.addWidget(self.vid_status)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.resize(600, 300)

        if csv_logging_enabled == 1:
            print("CSV logging enabled")
            self.csv_log_path = time.strftime("nano_log_%Y%m%d_%H%M%S.csv")
            self.log_path = time.strftime("my_log_%Y%m%d_%H%M%S.csv")
            self.new_file = not os.path.exists(self.log_path) or os.path.getsize(self.log_path) == 0
            self.csv_log_file = open(self.csv_log_path, "a", newline="")
            self.csv_writer = csv.writer(self.csv_log_file)
            if self.csv_log_file:
                self.csv_writer.writerow(["t", "L_encd", "R_encd, L_motor, R_motor"])

        # --- CREATING BUTTON FOR SENDING COMMANDS TO PI1 --- 
        # Setup Power Input
        self.pwr_input = QSpinBox()
        self.pwr_input.setRange(0, 150)
        self.pwr_input.setValue(100)
        self.pwr_input.setSuffix(" PWM")
        layout_btns.addWidget(self.pwr_input)

        # Create Buttons for Pi 1
        self.all_states = ["FWD", "LEFT", "RIGHT", "BACK", "STOP"]
        self.buttons = {}
        for state in self.all_states:
            btn = QPushButton(state)
            if state == "STOP":
                btn.clicked.connect(lambda _, s=state: self.send_cmd_pi1(s, 0))
            else:
                btn.clicked.connect(lambda _, s=state: self.send_cmd_pi1(s, self.pwr_input.value()))
            self.buttons[state] = btn
            layout_btns.addWidget(btn)

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.exit_gui)
        layout_btns.addWidget(self.exit_btn)

        self.en_vid_btn = QPushButton("Enable Video")
        self.dis_vid_btn = QPushButton("Disable Video")
        self.en_vid_btn.clicked.connect(self.enable_video_button)
        self.dis_vid_btn.clicked.connect(self.disable_video_button)
        layout_vid_btns.addWidget(self.en_vid_btn)
        layout_vid_btns.addWidget(self.dis_vid_btn)
        
        layout.addLayout( layout_btns )
        layout.addLayout( layout_nano )
        layout.addLayout( layout_elegoo )
        layout.addLayout( layout_vid_btns )

        # --- GUI Heartbeat timer --- 
        self.hb_timer = QTimer(self)
        self.hb_timer.timeout.connect(self.send_hb)
        self.hb_timer.start(self.interval_list["mac_pulse_read_interval"])   # In milliseconds; 100 ms = 10 Hz heartbeat

    # --- Exit button
    def exit_gui(self):
        self.send_cmd_pi1("STOP", 0)
        self.cmd_sent.setText("CMD:  EXIT")
        self.ffplay_start.terminate()
        QTimer.singleShot(500, self.shutdown_cmd)

        # --- Timer to read sockets
    def read_tm(self):
        readable, _, _ = select.select(self.read_tm_socket_list, [], [], 0)
        for s in readable:
            try:
                data, addr = s.recvfrom(2048)
            except BlockingIOError:
                continue
            json_conv_pkt = json.loads(data)
            src = dmm.json_reader(json_conv_pkt)
            if src == "nano":
                #print("Nano ", json_conv_pkt)
                self.f_uss, self.r_uss, self.l_uss, self.head, self.l_encd, self.r_encd, self.nano_id = dmm.nano_parser(json_conv_pkt)
                self.uss_f_status.setText(f"F_USS:  {self.f_uss}")
                self.uss_r_status.setText(f"R_USS:  {self.r_uss}")
                self.uss_l_status.setText(f"L_USS:  {self.l_uss}")
                self.head_status.setText(f"HEAD:   {self.head}")
                self.l_encd_status.setText(f"L_ENCD:  {self.l_encd}")
                self.r_encd_status.setText(f"R_ENCD:  {self.r_encd}")
                self.nano_id_status.setText(f"NANO ID:  {self.nano_id}")

            elif src == "elegoo":
                #print("ELEGOO ", json_conv_pkt)
                self.r_motor, self.l_motor, self.elegoo_id = dmm.elegoo_parser(json_conv_pkt)
                self.r_motor_status.setText(f"R_MOTOR:  {self.r_motor}")
                self.l_motor_status.setText(f"L_MOTOR:  {self.l_motor}")
                self.elegoo_id_status.setText(f"ELEGOO ID:  {self.elegoo_id}")

            if csv_logging_enabled == 1:
                self.generate_csv(self.csv_writer, self.csv_log_file, self.l_encd, self.r_encd, self.l_motor, self.r_motor)
        
    def send_cmd_pi1(self, cmd: str, pwr: int):
        pkt = {
            "source": "mac_cmd",
            "cmd": cmd,
            "pwr": pwr,
            "time": time.monotonic(),
            "mssg_id": 1
        }
        data = json.dumps(pkt).encode("utf-8")
        self.pi1_sock.sendto(data, (self.sendpoints["mac_cmd"][0], self.sendpoints["mac_cmd"][1]))
        self.cmd_sent.setText(f"CMD:  {cmd}")
        self.pwr_sent.setText(f"PWR:  {pwr}")

    def shutdown_cmd(self):
        pkt = {
            "source": "shutdown_cmd",
            "time": time.monotonic(),
        }
        data = json.dumps(pkt).encode("utf-8")
        self.pi1_sock.sendto(data, (self.sendpoints["shutdown_port"][0], self.sendpoints["shutdown_port"][1]))
        self.cmd_sent.setText("CMD:  SHUTDOWNNNNNNNNNN")
        QTimer.singleShot(200, self.close)

    def send_hb(self):
        pkt = {
            "source": "mac_pulse",
            "time": time.monotonic(),
            "pulse": "qqq"
        }
        data = json.dumps(pkt).encode("utf-8")
        self.pi1_sock.sendto(data, (self.sendpoints["mac_pulse"][0], self.sendpoints["mac_pulse"][1]))

    def start_video(self):
        # ffplay -fflags nobuffer -flags low_delay -framedrop -vf setpts=0 udp://192.168.1.72:5015
        video_streaming_link = (f"udp://{self.vid_ip}:{self.vid_port}")
        ffplay_cmd = ["ffplay", 
                    "-fflags", "nobuffer", 
                    "-flags", "low_delay",
                     "-framedrop", 
                     "-vf", "setpts=0",
                    video_streaming_link]
        self.ffplay_start = subprocess.Popen(ffplay_cmd)

    def enable_video_button(self): # Sends JSON mssg to pi to enable video stream
        print("enable!")
        self.vid_status.setText("Video Status:  Enabled")
        self.start_video()
        #pass

    def disable_video_button(self):  # Sends JSON mssg to pi to disable video stream
        print("disable!")
        self.vid_status.setText("Video Status:  Disabled")
        self.ffplay_start.terminate()
        #pass

    def generate_csv(self, csv_writer: csv.writer, csv_log_file, l_encd: int, r_encd: int, l_motor: int, r_motor: int):
        csv_writer.writerow([
            time.monotonic(),
            l_encd,
            r_encd,
            l_motor,
            r_motor
        ])
        csv_log_file.flush()
        os.fsync(csv_log_file.fileno())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CmdGUI()
    win.show()
    sys.exit(app.exec())