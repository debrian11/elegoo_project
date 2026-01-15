#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304. C0411, E0401
# Python Script for GUI
import json
import socket
import select
import sys
import time
import m_data_mgr_module as dmm
import m_yaml_data as yd

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QVBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QWidget, QMainWindow)

class CmdGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Parse out the yml to grab the ports
        self.yaml_file_name = 'pi_config.yml'
        self.parsed_out_yml = dmm.parse_yaml(self.yaml_file_name)

        # Read Sockets
        self.read_tm_socket_list = yd.read_tm_sockets(self.parsed_out_yml, 0)
        self.tm_timer = QTimer(self)
        self.tm_timer.timeout.connect(self.read_tm) # implement the read tm
        self.tm_timer.start(50) # ms   

        # TX Sockets
        ip_setting = 0
        self.sendpoints = yd.send_ports(self.parsed_out_yml, ip_setting)
        self.interval_list = yd.intervals_read_send(self.parsed_out_yml)
        self.pi1_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # --- Create UI Layout ---
        self.setWindowTitle("Pi Bot Command GUI")
        layout =        QHBoxLayout()
        layout_nano =   QVBoxLayout()
        layout_elegoo = QVBoxLayout()
        layout_btns =   QVBoxLayout()

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

        # Elegoo TM Data
        self.l_motor_status     = QLabel("MOTOR L:  N/A")
        self.r_motor_status     = QLabel("MOTOR R:  N/A")
        self.elegoo_id_status   = QLabel("ELEGOO ID:  N/A")

        #layout.addWidget(self.status)
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

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.resize(600, 300)

        # --- CREATING BUTTON FOR SENDING COMMANDS TO PI1 --- 
        # Setup Power Input
        self.pwr_input = QSpinBox()
        self.pwr_input.setRange(0, 100)
        self.pwr_input.setValue(100)
        self.pwr_input.setSuffix(" %")
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
        
        layout.addLayout( layout_btns )
        layout.addLayout( layout_nano )
        layout.addLayout( layout_elegoo )

        # --- GUI Heartbeat timer --- 
        self.hb_timer = QTimer(self)
        self.hb_timer.timeout.connect(self.send_hb)
        self.hb_timer.start(self.interval_list["mac_pulse_read_interval"])   # In milliseconds; 100 ms = 10 Hz heartbeat

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
                f_uss, r_uss, l_uss, head, l_encd, r_encd, nano_id = dmm.nano_parser(json_conv_pkt)
                self.uss_f_status.setText(f"USS F:  {f_uss}")
                self.uss_r_status.setText(f"USS R:  {r_uss}")
                self.uss_l_status.setText(f"USS L:  {l_uss}")
                self.head_status.setText(f"HEAD:   {head}")
                self.l_encd_status.setText(f"L_ENCD:  {l_encd}")
                self.r_encd_status.setText(f"R_ENCD:  {r_encd}")
                self.nano_id_status.setText(f"NANO ID:  {nano_id}")

            elif src == "elegoo":
                #print("ELEGOO ", json_conv_pkt)
                r_motor, l_motor, elegoo_id = dmm.elegoo_parser(json_conv_pkt)
                self.r_motor_status.setText(f"MOTOR L:  {r_motor}")
                self.l_motor_status.setText(f"MOTOR R:  {l_motor}")
                self.elegoo_id_status.setText(f"ELEGOO ID:  {elegoo_id}")

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

    def send_hb(self):
        pkt = {
            "source": "mac_pulse",
            "time": time.monotonic(),
            "pulse": "qqq"
        }
        data = json.dumps(pkt).encode("utf-8")
        self.pi1_sock.sendto(data, (self.sendpoints["mac_pulse"][0], self.sendpoints["mac_pulse"][1]))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CmdGUI()
    win.show()
    sys.exit(app.exec())