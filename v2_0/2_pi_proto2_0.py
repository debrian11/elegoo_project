#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304
import socket
import serial
import os
import select
import json
import time
import m_data_mgr_module as data_mgr
import m_data_responder_module as drm
import m_yaml_data as yd

# ------ SETTINGS ------- #
# Set if testing locally or on hardware. This sets the IP for the socket
# 0 = local
# 1 = on pi
test_setting = 0

# Serial Ports
# Set this to enable serial ports:
# 0 = none
# 1 = Elegoo only
# 2 = Nano only
# 3 = Elegoo and Nano
serial_port_setting = 0

# set true if wanting to print stuff
print_stuff = 1
print_wait = 0.1


# ------ end SETTINGS ---- #

yaml_file_name = 'pi_config.yml'

def elegoo_serial_setup():
    ELEGOO_PORT = '/dev/arduino_elegoo'
    while True:
        if not os.path.exists(ELEGOO_PORT):
            print(f"{ELEGOO_PORT} not connected, retrying...")
            time.sleep(1.0)
            continue
        elif os.path.exists(ELEGOO_PORT):
            pi_elegoo_port = serial.Serial(port=ELEGOO_PORT, baudrate= 115200, timeout=1.0)
            time.sleep(3.0)
            pi_elegoo_port.reset_input_buffer()
            print(F"Connected to ELEGOO port at {ELEGOO_PORT}")
            return pi_elegoo_port

def nano_serial_setup():
    NANO_PORT = '/dev/arduino_nano'
    while True:
        if not os.path.exists(NANO_PORT):
            print(f"{NANO_PORT} not connected, retrying...")
            time.sleep(1.0)
            continue
        elif os.path.exists(NANO_PORT):
            pi_nano_port = serial.Serial(port=NANO_PORT, baudrate= 115200, timeout=1.0)
            time.sleep(3.0)
            pi_nano_port.reset_input_buffer()
            print(F"Connected to NANO port at {NANO_PORT}")
            return pi_nano_port
        

def myfunction():
    if print_stuff == 1:
        print("Starting script")
        time.sleep(print_wait)
    counter = 0

    if print_stuff == 1:
        print("Setting initial values")
        time.sleep(print_wait)
    f_uss, r_uss, l_uss, head, l_encd, r_encd, l_motor, r_motor, cmd, pwr,  = data_mgr.initial_values()
    mac_pulse_time_rvd, pi2_pulse_time_rvd, nano_time, elegoo_time, mac_cmd_time, last_mac_cmd_time_rcv, last_mac_pulse_time_rcv, last_time_turned = data_mgr.initial_time_values()
    mac_pulse_mssg_id, pi2_pulse_mssg_id, nano_id, elegoo_id, mac_cmd_id = data_mgr.initial_mssg_id_values()

    # Parse the yaml
    if print_stuff == 1:
        print("Parsing values from yaml")
        time.sleep(print_wait)
    parsed_out_yaml = data_mgr.parse_yaml(yaml_file_name)
    interval_list = yd.intervals_read_send(parsed_out_yaml)

    # Intialize RX and TX sockets
    if print_stuff == 1:
        print("Setting up sockets")
        time.sleep(print_wait)
    link_checker = False
    new_cmd = False
    turning = False
    done_turning = True
    sock_list = yd.assign_read_sockets(parsed_out_yaml, test_setting)
    time.sleep(2)
    tx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mtr_cmd = drm.fallback_motor_cmd("STOP", 0)

    if print_stuff == 1:
        print("Connecting to serial port")
        time.sleep(print_wait)

    # Serial port initialize
    if serial_port_setting == 1 or serial_port_setting == 3:
        elegoo_port = elegoo_serial_setup()

    elif serial_port_setting == 2 or serial_port_setting == 3:
        nano_port = nano_serial_setup()

    elif serial_port_setting == 3:
        elegoo_port = elegoo_serial_setup()
        nano_port = nano_serial_setup()

    if print_stuff == 1:
        print("Begin the loop")
        time.sleep(print_wait)

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

            elif src == "elegoo":
                r_motor, l_motor, elegoo_time, elegoo_id = data_mgr.elegoo_parser(data_to_json)
                #print("ELEGOO RXd", counter, data_to_json)

            elif src == "mac_cmd":
                cmd, pwr, mac_cmd_time, mac_cmd_id = data_mgr.mac_parser(data_to_json)
                last_mac_cmd_time_rcv = time.monotonic()
                #print("MAC CMD", counter, data_to_json)

            elif src == "mac_pulse":
                mac_pulse_time_rvd, mac_pulse_mssg_id = data_mgr.read_mac_heartbeat(data_to_json)
                last_mac_pulse_time_rcv = time.monotonic()
                #print("MAC PULSE", counter, data_to_json)
        
            elif src == "pi2_pulse":
                pi2_pulse_mssg_id, pi2_pulse_time_rvd = data_mgr.read_pi2_heartbeat(data_to_json)
                #print("PI2_pulse", counter, data_to_json)
        # --- End Read ports --- #
        

        # --- Mac laptop and cmd checker --- #
        link_checker = drm.mac_hb_checker(last_mac_pulse_time_rcv, current_time, interval_list["mac_hb_timeout"])
        new_cmd = drm.cmd_timeout_checker(cmd, last_mac_cmd_time_rcv, current_time, interval_list["mac_cmd_timeout"])
        # --- End Mac laptop and cmd checker --- #
        
        
        # --- Perform cmds based on link or cmd tieout --- #
        if link_checker is False:
            mtr_cmd = drm.fallback_motor_cmd("STOP", 0)
            if serial_port_setting == 1 or serial_port_setting == 3:
                elegoo_port.write((mtr_cmd + "\n").encode("utf-8"))
            
        elif link_checker is True:
            if new_cmd is True:
                #mtr_cmd = drm.motor_cmd_UDP(cmd, pwr)
                mtr_cmd, last_time_turned, done_turning, turning = drm.motor_cmd(cmd, pwr, turning, done_turning, f_uss, l_uss, r_uss, last_time_turned, current_time, mtr_cmd)
                if serial_port_setting == 1 or serial_port_setting == 3:
                    elegoo_port.write((mtr_cmd + "\n").encode("utf-8"))

            elif new_cmd is False:
                mtr_cmd = drm.fallback_motor_cmd("STOP", 0)
                if serial_port_setting == 1 or serial_port_setting == 3:
                    elegoo_port.write((mtr_cmd + "\n").encode("utf-8"))

        if print_stuff == 1:
            print("Link = ", link_checker, "  Cmd timeout = ", new_cmd, "  MTR = ", mtr_cmd, "  turn delta", current_time - last_time_turned, "  done_turning", done_turning, "  turning", turning)
            #print("MTR = ", mtr_cmd, "  turn delta", current_time - last_time_turned, "  done_turning", done_turning, "  turning", turning)
        # --- End Perform cmds based on link or cmd tieout --- #


        time.sleep(0.001)

if __name__ == "__main__":
    myfunction()