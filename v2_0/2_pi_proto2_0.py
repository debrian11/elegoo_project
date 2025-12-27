#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304
import socket
import serial
import os
import select
import json
import time
import data_mgr_module as data_mgr
import data_responder_module as drm
import yaml_data as yd


# Set if testing locally or on hardware
# 0 = local
# 1 = on hardware
test_setting = 0

yaml_file_name = 'pi_config.yml'
def serial_setup():
    ELEGOO_PORT = '/dev/arduino_elegoo'
    NANO_PORT = '/dev/arduino_nano'

    while True:
        if not os.path.exists(ELEGOO_PORT):
            print(f"{ELEGOO_PORT} not connected, retrying...")
            time.sleep(1.0)
            continue
        elif os.path.exists(ELEGOO_PORT):
            pi_elegoo_port = serial.Serial(port=ELEGOO_PORT, baudrate= 115200, timeout=1.0)
            time.sleep(3.0)
            pi_elegoo_port.reset_input_buffer()
            return pi_elegoo_port


def myfunction():
    print("Initializing")
    counter = 0

    f_uss, r_uss, l_uss, head, l_encd, r_encd, l_motor, r_motor, cmd, pwr,  = data_mgr.initial_values()
    mac_pulse_time_rvd, pi2_pulse_time_rvd, nano_time, elegoo_time, mac_cmd_time, last_mac_cmd_time_rcv, last_mac_pulse_time_rcv = data_mgr.initial_time_values()
    mac_pulse_mssg_id, pi2_pulse_mssg_id, nano_id, elegoo_id, mac_cmd_id = data_mgr.initial_mssg_id_values()

    # Parse the yaml
    parsed_out_yaml = data_mgr.parse_yaml(yaml_file_name)
    interval_list = yd.intervals_read_send(parsed_out_yaml)

    # Intialize RX and TX sockets
    link_checker = False
    cmd_timeout = False
    sock_list = yd.assign_read_sockets(parsed_out_yaml, test_setting)
    tx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mtr_cmd = drm.motor_cmd_UDP("STOP", 0)

    print("connect to serial port")
    if test_setting == 1:
        elegoo_port = serial_setup()
    print("Begin loop")

    # --- Read the data ---
    # Initialize TX Socket
    while True:
        current_time = time.monotonic()
        counter += 1

        # --- Read ports --- #
        read_ports, _, _ = select.select(sock_list, [], [], 0.02) # 20 ms timeout
        for s in read_ports:
            last_pkt = None
            while True:
                try:
                    data, addr = s.recvfrom(2048)   # Data comes in as string
                except BlockingIOError:
                    break
                last_pkt = data

            if last_pkt is None:
                continue

            data_to_json = json.loads(last_pkt) # Convert string to json
            src = data_mgr.json_reader(data_to_json)

            if src == "nano":
                f_uss, r_uss, l_uss, head, l_encd, r_encd, nano_time, nano_id = data_mgr.nano_parser(data_to_json)
                #print("NANO RXd", counter, data_to_json)

            if src == "elegoo":
                r_motor, l_motor, elegoo_time, elegoo_id = data_mgr.elegoo_parser(data_to_json)
                #print("ELEGOO RXd", counter, data_to_json)

            if src == "mac_cmd":
                cmd, pwr, mac_cmd_time, mac_cmd_id = data_mgr.mac_parser(data_to_json)
                last_mac_cmd_time_rcv = time.monotonic()
                #print("MAC CMD", counter, data_to_json)

            if src == "mac_pulse":
                mac_pulse_time_rvd, mac_pulse_mssg_id = data_mgr.read_mac_heartbeat(data_to_json)
                last_mac_pulse_time_rcv = time.monotonic()
                #print("MAC PULSE", counter, data_to_json)
        
            if src == "pi2_pulse":
                pi2_pulse_mssg_id, pi2_pulse_time_rvd = data_mgr.read_pi2_heartbeat(data_to_json)
                #print("PI2_pulse", counter, data_to_json)
        # --- End Read ports --- #
        

        # --- Mac laptop and cmd checker --- #
        link_checker = drm.mac_hb_checker(last_mac_pulse_time_rcv, current_time, interval_list["mac_hb_timeout"])
        cmd_timeout = drm.cmd_timeout_checker(cmd, last_mac_cmd_time_rcv, current_time, interval_list["mac_cmd_timeout"])
        # --- End Mac laptop and cmd checker --- #
        
        
        # --- Perform cmds based on link or cmd tieout --- #
        if link_checker is False:
            mtr_cmd = drm.motor_cmd_UDP("STOP", 0)
            if test_setting == 1:
                elegoo_port.write((mtr_cmd + "\n").encode("utf-8"))
            
        elif link_checker is True:
            if cmd_timeout is True:
                mtr_cmd = drm.motor_cmd_UDP(cmd, pwr)
                drm.uss_mover(f_uss, r_uss, l_uss, current_time)
                drm.heading_keeper(head, current_time)
                if test_setting == 1:
                    elegoo_port.write((mtr_cmd + "\n").encode("utf-8"))

            elif cmd_timeout is False:
                mtr_cmd = drm.motor_cmd_UDP("STOP", 0)
                if test_setting == 1:
                    elegoo_port.write((mtr_cmd + "\n").encode("utf-8"))


        print("Link = ", link_checker, "  Cmd timeout = ", cmd_timeout, "  MTR = ", mtr_cmd)
        # --- End Perform cmds based on link or cmd tieout --- #

if __name__ == "__main__":
    myfunction()