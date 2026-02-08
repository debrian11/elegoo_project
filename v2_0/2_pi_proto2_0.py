#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304, C0411. C0321
# Description: Main python code for the Pi. Orchestrates the logic of the robot
# Initializes sockets and serial ports depending on test configuration set in the SETTINGS section
# Parses out UDP ports and/or serial ports into repsective parsers
# Sends JSON message packets over serial / UDP for motor control
# Sends Motor and Sensor data out on UDP packet to GUI

import socket
import os
import select
import json
import time
import sys
import argparse
import m_serial_handler         as sh       # Configures serial ports
import m_data_mgr_module        as data_mgr # Manages parsers of received JSON packets depending on source
import m_data_responder_module  as drm      # Manages responses to send
import m_yaml_data              as yd       # Parses out yaml configuration file
import m_initial_values         as iv       # Manages initial values
import m_video_stream           as vs       # Video stream module



# ----- Arguement Parser ------- #
the_parser = argparse.ArgumentParser(
    description="Sets IP and Port settings"
)
the_parser.add_argument('-i', '--ip',          type=int, default=0)  # [0] = local IP   |    [1] = Pi IP  
the_parser.add_argument('-s', '--serialport',  type=int, default=0) # [0] = none(UDP)  |  [1] = Elegoo  |  [2] = Nano  |   [3] Elegoo & Nano
the_parser.add_argument('-c', '--csv',         type=int, default=0) # [0] = OFF   |    [1] = ON    
the_parser.add_argument('-p', '--printstuff',  type=int, default=0) # [0] = no print   |    [1] = print    
the_parser.add_argument('-v', '--vid',         type=int, default=0) # [0] = Dis Vid Strm   |    [1] = En Vid Strm

# Parse the args
args = the_parser.parse_args()

ip_setting = args.ip
serial_port_setting = args.serialport
csv_logging = args.csv
print_stuff = args.printstuff
video_setting = args.vid
print("Initial Settings:")
print("ip_setting = ", ip_setting)
print("serial_port_setting = ", serial_port_setting)
print("csv_logging = ", csv_logging)
print("print_stuff = ", print_stuff)
print("video_setting = ", video_setting)

# ------ SETTINGS ------- #
# [0] = local IP   |    [1] = Pi IP                           # Set if testing locally or on hardware. This sets the IP for the socket
# [0] = none  |  [1] = Elegoo  |  [2] = Nano  |   [3] = Elegoo & Nano # Set this to enable serial ports:
# [0] = OFF   |    [1] = ON                                   # Set this to enable CSV Logging
# [0] = no print   |    [1] = print                           # set true if wanting to print stuff
# [0] = UDP Test Tool   |    [1] = Nano HW                    # Set this to enable commanding motors based on 
#                                                               Sensor data from UDP Test Tool or Nano HW
# [0] = UDP Test Tool   |    [1] = Elegoo HW                  # Set this to enable test Elegoo or HW
# [0] = Disable Video Stream   |    [1] = Enable Video Stream # Set this to enable video stream at /dev/video0
print_wait = 0.1  

# ------ end SETTINGS ---- #

yaml_file_name = 'pi_config.yml'
log_path = time.strftime("csv_files/my_log_%Y%m%d_%H%M%S.csv")
ELEGOO_PORT = '/dev/arduino_elegoo'
NANO_PORT = '/dev/arduino_nano'
camera_path = '/dev/video0'

def myfunction():
    try:
        if print_stuff == 1: print("Starting script"); time.sleep(print_wait); print("Setting initial values"); time.sleep(print_wait)

        # Initial Values
        f_uss, r_uss, l_uss, head, l_encd, r_encd, l_motor, r_motor, cmd, pwr, tgt_heading = iv.initial_values()
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
        if print_stuff == 1: print("Setting Read sockets"); time.sleep(print_wait)
        sock_list = yd.assign_read_sockets(parsed_out_yaml, ip_setting)
        time.sleep(0.5)
        if print_stuff == 1: print("Setting TX sockets"); time.sleep(print_wait)
        tx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tm_sendpoints = yd.send_tm_ports(parsed_out_yaml, ip_setting)
        time.sleep(0.5)

        mtr_cmd = drm.fallback_motor_cmd("STOP", 0)
        # --- End Intialize RX and TX sockets --- #

        # --- Video Stream Settings --- #
        if video_setting == 1:
            if os.path.exists(camera_path):
                stream_video = vs.pi_video_stream(camera_path, tm_sendpoints["pi_to_mac_vid"][0], tm_sendpoints["pi_to_mac_vid"][1])

        # --- Initialize Serial Ports --- #
        elegoo_ser_buffer = ""
        nano_ser_buffer = ""
        if serial_port_setting == 0:
            nano_setting = 0                    # [0] = UDP Test Tool   |    [1] = Nano HW 
            elegoo_setting = 0                  # [0] = UDP Test Tool   |    [1] = Elegoo HW 
            print("Skipping serial setup")

        elif serial_port_setting == 1:
            elegoo_port = sh.serial_port_setup(port_name=ELEGOO_PORT, baud_rate=115200)
            nano_setting = 1
            elegoo_setting = 1
            print("Connecting to both Nano Port"); print(elegoo_port)

        elif serial_port_setting == 2:
            nano_port = sh.serial_port_setup(port_name=NANO_PORT, baud_rate=115200)
            nano_setting = 1
            elegoo_setting = 1
            print("Connecting to both Nano Port"); print(nano_port)

        elif serial_port_setting == 3:
            elegoo_port = sh.serial_port_setup(port_name=ELEGOO_PORT, baud_rate=115200)
            nano_port = sh.serial_port_setup(port_name=NANO_PORT, baud_rate=115200)
            nano_setting = 1
            elegoo_setting = 1
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
                        f_uss, r_uss, l_uss, head, l_encd, r_encd, nano_id = data_mgr.nano_parser(data_to_json)
                        print("NANO-UDP :", data_to_json)
                        tx_socket.sendto(last_pkt, (tm_sendpoints["nano_to_mac"][0], tm_sendpoints["nano_to_mac"][1]))

                if elegoo_setting == 0:
                    if src == "elegoo":
                        r_motor, l_motor, elegoo_id = data_mgr.elegoo_parser(data_to_json)
                        print("ELEGOO RXd", data_to_json)
                        tx_socket.sendto(last_pkt, (tm_sendpoints["elegoo_to_mac"][0], tm_sendpoints["elegoo_to_mac"][1]))

                if src == "mac_cmd":
                    cmd, pwr, mac_cmd_time, mac_cmd_id = data_mgr.mac_parser(data_to_json)
                    last_mac_cmd_time_rcv = time.monotonic()
                    #print("mac_cmd", data_to_json)

                elif src == "mac_pulse":
                    mac_pulse_time_rvd, mac_pulse_mssg_id = data_mgr.read_mac_heartbeat(data_to_json)
                    last_mac_pulse_time_rcv = time.monotonic()
                    #print("mac_pulse", data_to_json)
                
                elif src =="vid_cmd":
                    pass

                elif src == "shutdown_cmd":
                    mtr_cmd = drm.fallback_motor_cmd("STOP", 0)
                    if serial_port_setting == 0:
                        mtr_str_to_json = json.loads(mtr_cmd)
                        udp_mtr_cmd = { "source" : "mtr_cmd", **mtr_str_to_json}
                        tx_socket.sendto(data_mgr.json_convert(udp_mtr_cmd), (tm_sendpoints["pi_to_sim_mtr"][0], tm_sendpoints["pi_to_sim_mtr"][1]))
                        time.sleep(0.1)
                        sys.exit()

                    if serial_port_setting == 1 or serial_port_setting == 3:
                        sh.write_json(elegoo_port, mtr_cmd)

                elif src == "pi2_pulse":
                    pi2_pulse_mssg_id, pi2_pulse_time_rvd = data_mgr.read_pi2_heartbeat(data_to_json)
            # --- End Read UDP ports --- #
          

            # --- Read Serial Ports then sends it over TM --- #
            # Elegoo
            if serial_port_setting == 1 or serial_port_setting == 3:
                elegoo_json, elegoo_ser_buffer = sh.read_json(elegoo_port, elegoo_ser_buffer)
                if isinstance(elegoo_json, dict):
                    r_motor, l_motor, elegoo_id = data_mgr.elegoo_parser(elegoo_json)
                    final_elegoo_json = { "source": "elegoo", **elegoo_json}
                    tx_socket.sendto(data_mgr.json_convert(final_elegoo_json), (tm_sendpoints["elegoo_to_mac"][0], tm_sendpoints["elegoo_to_mac"][1]))

            # Nano
            if serial_port_setting == 2 or serial_port_setting == 3:
                nano_json, nano_ser_buffer = sh.read_json(nano_port, nano_ser_buffer)
                if isinstance(nano_json, dict):
                    if nano_setting == 1:
                        f_uss, r_uss, l_uss, head, l_encd, r_encd, nano_id = data_mgr.nano_parser(nano_json)
                        final_nano_json = { "source": "nano", **nano_json}
                        tx_socket.sendto(data_mgr.json_convert(final_nano_json), (tm_sendpoints["nano_to_mac"][0], tm_sendpoints["nano_to_mac"][1]))

            # --- Mac laptop and cmd checker --- #
            link_checker = drm.mac_hb_checker(last_mac_pulse_time_rcv, current_time, interval_list["mac_hb_timeout"])
            new_cmd = drm.cmd_timeout_checker(cmd, last_mac_cmd_time_rcv, current_time, interval_list["mac_cmd_timeout"])
            # --- End Mac laptop and cmd checker --- #
            
            # --- Motor Commands --- #
            if link_checker is False:
                mtr_cmd = drm.fallback_motor_cmd("STOP", 0) # mtr_cmd is a json str
                if serial_port_setting == 1 or serial_port_setting == 3:
                    sh.write_json(elegoo_port, mtr_cmd)
                if ip_setting == 0:
                    mtr_str_to_json = json.loads(mtr_cmd)
                    udp_mtr_cmd = { "source" : "mtr_cmd", **mtr_str_to_json}
                    tx_socket.sendto(data_mgr.json_convert(udp_mtr_cmd), (tm_sendpoints["pi_to_sim_mtr"][0], tm_sendpoints["pi_to_sim_mtr"][1]))
                    #print(udp_mtr_cmd)
                
            elif link_checker is True:
                if new_cmd is True:
                    mtr_cmd, last_time_turned, done_turning, turning = drm.motor_cmd(cmd, pwr, turning, done_turning, f_uss, l_uss, r_uss, 
                                                                                    tgt_heading, head, last_time_turned, current_time, mtr_cmd, 
                                                                                    interval_list["f_uss_threshold"], interval_list["l_uss_threshold"], 
                                                                                    interval_list["r_uss_threshold"], interval_list["turn_time_threshold"])
                    if serial_port_setting == 1 or serial_port_setting == 3:
                        sh.write_json(elegoo_port, mtr_cmd)
                    if ip_setting == 0:
                        mtr_str_to_json = json.loads(mtr_cmd)
                        udp_mtr_cmd = { "source" : "mtr_cmd", **mtr_str_to_json}
                        tx_socket.sendto(data_mgr.json_convert(udp_mtr_cmd), (tm_sendpoints["pi_to_sim_mtr"][0], tm_sendpoints["pi_to_sim_mtr"][1]))
                        #print(udp_mtr_cmd)

                elif new_cmd is False:
                    mtr_cmd = drm.fallback_motor_cmd("STOP", 0)
                    if serial_port_setting == 1 or serial_port_setting == 3:
                        sh.write_json(elegoo_port, mtr_cmd)
                    if ip_setting == 0:
                        mtr_str_to_json = json.loads(mtr_cmd)
                        udp_mtr_cmd = { "source" : "mtr_cmd", **mtr_str_to_json}
                        tx_socket.sendto(data_mgr.json_convert(udp_mtr_cmd), (tm_sendpoints["pi_to_sim_mtr"][0], tm_sendpoints["pi_to_sim_mtr"][1]))
                        #print(udp_mtr_cmd)

            # --- End Perform cmds based on link or cmd timeout --- #

            time.sleep(0.001)
    except KeyboardInterrupt:
        print("\Shutting Down")
    
    finally:
        if serial_port_setting == 3:
            elegoo_port.close()
            nano_port.close()
        if video_setting == 1:
            if os.path.exists(camera_path):
                stream_video.terminate()
                stream_video.wait()

if __name__ == "__main__":
    myfunction()