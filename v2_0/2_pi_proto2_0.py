#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304, C0411. C0321
import socket
import serial
import os
import select
import json
import time
import m_serial_handler as sh
import m_data_mgr_module as data_mgr
import m_data_responder_module as drm
import m_yaml_data as yd
import m_initial_values as iv

# ------ SETTINGS ------- #
# Set if testing locally or on hardware. This sets the IP for the socket
# [0] = local IP   |    [1] = Pi IP
ip_setting = 0

# Set this to enable CSV Logging
# [0] = OFF   |    [1] = ON
csv_logging = 0

# Set this to enable serial ports:
# [0] = none  |  [1] = Elegoo  |  [2] = Nano  |   [3] = Elegoo & Nano
serial_port_setting = 0

# set true if wanting to print stuff
print_stuff = 1; print_wait = 0.1

# Set this to enable commanding motors based on Sensor data from UDP Test Tool or Nano HW
# [0] = UDP Test Tool   |    [1] = Nano HW
nano_setting = 0
# ------ end SETTINGS ---- #

yaml_file_name = 'pi_config.yml'
log_path = time.strftime("csv_files/my_log_%Y%m%d_%H%M%S.csv")
ELEGOO_PORT = '/dev/arduino_elegoo'
NANO_PORT = '/dev/arduino_nano'

def myfunction():
    if print_stuff == 1: print("Starting script"); time.sleep(print_wait); print("Setting initial values"); time.sleep(print_wait)

    f_uss, r_uss, l_uss, head, l_encd, r_encd, l_motor, r_motor, cmd, pwr,  = iv.initial_values()
    mac_pulse_time_rvd, pi2_pulse_time_rvd, mac_cmd_time, last_mac_cmd_time_rcv, last_mac_pulse_time_rcv, last_time_turned = iv.initial_time_values()
    mac_pulse_mssg_id, pi2_pulse_mssg_id, nano_id, elegoo_id, mac_cmd_id = iv.initial_mssg_id_values()
    link_checker, new_cmd, turning, done_turning = iv.intial_boolean_values()
    # --- CSV logger --- #
    if csv_logging == 1:
        csv_write = data_mgr.csv_logger(log_path)
    
    # --- Parse the yaml --- #
    if print_stuff == 1: print("Parsing values from yaml"); time.sleep(print_wait)
    parsed_out_yaml = data_mgr.parse_yaml(yaml_file_name)
    interval_list = yd.intervals_read_send(parsed_out_yaml)
    # --- End Parse the yaml --- #

    # --- Intialize RX and TX sockets --- #
    if print_stuff == 1: print("Setting up sockets"); time.sleep(print_wait)
    sock_list = yd.assign_read_sockets(parsed_out_yaml, ip_setting)
    time.sleep(2)
    tx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mtr_cmd = drm.fallback_motor_cmd("STOP", 0)
    # --- End Intialize RX and TX sockets --- #

    # --- Initialize Serial Ports --- #
    elegoo_ser_buffer = ""
    nano_ser_buffer = ""
    if print_stuff == 1:
        print("Connecting to serial port"); time.sleep(print_wait)

    if serial_port_setting == 1:
        elegoo_port = sh.serial_port_setup(port_name=ELEGOO_PORT, baud_rate=115200)
        print("Connecting to both Nano Port"); print(elegoo_port)

    elif serial_port_setting == 2:
        nano_port = sh.serial_port_setup(port_name=NANO_PORT, baud_rate=115200)
        print("Connecting to both Nano Port"); print(nano_port)

    elif serial_port_setting == 3:
        elegoo_port = sh.serial_port_setup(port_name=ELEGOO_PORT, baud_rate=115200)
        nano_port = sh.serial_port_setup(port_name=NANO_PORT, baud_rate=115200)
        print("Connecting to both Serial Ports")
        print(nano_port); print(elegoo_port)
        time.sleep(0.5)
    # --- End Initialize Serial Ports --- #

    # --- ** Main Loop ** --- #
    if print_stuff == 1: print("Begin the loop"); time.sleep(print_wait)
    while True:
        t0 = time.monotonic()
        current_time = time.monotonic()

        # --- Read UDP ports --- #
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

            if nano_setting == 0:
                if src == "nano":
                    f_uss, r_uss, l_uss, head, l_encd, r_encd, nano_time, nano_id = data_mgr.nano_parser(data_to_json)
                    #print("NANO RXd", data_to_json)

            #if src == "elegoo":
                #r_motor, l_motor, elegoo_time, elegoo_id = data_mgr.elegoo_parser(data_to_json)
                ##print("ELEGOO RXd", data_to_json)

            if src == "mac_cmd":
                cmd, pwr, mac_cmd_time, mac_cmd_id = data_mgr.mac_parser(data_to_json)
                last_mac_cmd_time_rcv = time.monotonic()
                #print("MAC CMD", data_to_json)

            elif src == "mac_pulse":
                mac_pulse_time_rvd, mac_pulse_mssg_id = data_mgr.read_mac_heartbeat(data_to_json)
                last_mac_pulse_time_rcv = time.monotonic()
                #print("MAC PULSE", data_to_json)
        
            elif src == "pi2_pulse":
                pi2_pulse_mssg_id, pi2_pulse_time_rvd = data_mgr.read_pi2_heartbeat(data_to_json)
                #print("PI2_pulse", data_to_json)
        t1 = time.monotonic()
        # --- End Read UDP ports --- #

        # --- Read Serial Ports --- #
        # Elegoo
        if serial_port_setting == 1 or serial_port_setting == 3:
            #elegoo_json = sh.readline_json(elegoo_port) ; print("ELEGOO: ", elegoo_json)
            elegoo_json, elegoo_ser_buffer = sh.read_json(elegoo_port, elegoo_ser_buffer)
            if isinstance(elegoo_json, dict):
                r_motor, l_motor, elegoo_id = data_mgr.elegoo_parser(elegoo_json)

        # Nano
        if serial_port_setting == 2 or serial_port_setting == 3:
            #nano_json = sh.readline_json(nano_port) ; print("NANO: ", nano_json)
            nano_json, nano_ser_buffer = sh.read_json(nano_port, nano_ser_buffer)
            if isinstance(nano_json, dict):
                if nano_setting == 1:
                    f_uss, r_uss, l_uss, head, l_encd, r_encd, nano_id = data_mgr.nano_parser(nano_json)

        # --- Mac laptop and cmd checker --- #
        link_checker = drm.mac_hb_checker(last_mac_pulse_time_rcv, current_time, interval_list["mac_hb_timeout"])
        new_cmd = drm.cmd_timeout_checker(cmd, last_mac_cmd_time_rcv, current_time, interval_list["mac_cmd_timeout"])
        t2 = time.monotonic()
        # --- End Mac laptop and cmd checker --- #
        
        # --- Perform cmds based on link or cmd tieout --- #
        if link_checker is False:
            mtr_cmd = drm.fallback_motor_cmd("STOP", 0)
            if serial_port_setting == 1 or serial_port_setting == 3:
                #elegoo_port.write((mtr_cmd + "\n").encode("utf-8"))
                sh.write_json(elegoo_port, mtr_cmd)
            
        elif link_checker is True:
            if new_cmd is True:
                mtr_cmd, last_time_turned, done_turning, turning = drm.motor_cmd(cmd, pwr, turning, done_turning, f_uss, l_uss, r_uss, last_time_turned, current_time, mtr_cmd)
                if serial_port_setting == 1 or serial_port_setting == 3:
                    #elegoo_port.write((mtr_cmd + "\n").encode("utf-8"))
                    sh.write_json(elegoo_port, mtr_cmd)

            elif new_cmd is False:
                mtr_cmd = drm.fallback_motor_cmd("STOP", 0)
                if serial_port_setting == 1 or serial_port_setting == 3:
                    #elegoo_port.write((mtr_cmd + "\n").encode("utf-8"))
                    sh.write_json(elegoo_port, mtr_cmd)
        t3 = time.monotonic()

        # --- End Perform cmds based on link or cmd timeout --- #
        time.sleep(0.001)

if __name__ == "__main__":
    myfunction()