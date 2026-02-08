#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304. C0411
# This script will simulate the ouput of the Elegoo and Nano portions
# Encoder testing data reference:
# PWM     50              100             150
# L Encd  69.75429568	  130.0175577     203.0123211
# R Encd  68.46070675	  123.2839752	  194.4117992
# % Diff   1.88953488       5.4618473	    4.4238683
# avg L ticks/pwm = 1.349558988
# avg R ticks/pwm = 1.299377516

import json
import time
import math
import select
import socket
import argparse
import m_initial_values as iv
import m_data_mgr_module as dmm
import m_yaml_data as yd

the_arg_parser = argparse.ArgumentParser(
    description="Sets the IP of data sent to either local or Pi"
)
the_arg_parser.add_argument('-i', "--ipsetting",  type=int, default=0)
parsed_args = the_arg_parser.parse_args()
ip_setting = parsed_args.ipsetting
print("ip_setting = ", ip_setting)

yaml_file_name = 'pi_config.yml'
#ip_setting = 0 # 0 = Local | 1 = Pi

def l_encd_math(pwm, encd):
    if pwm > 0:
        encd = encd + 1.35
        return math.ceil(encd)
    else:
        return encd

def r_encd_math(pwm, encd):
    if pwm > 0:
        encd = encd + 1.35
        return math.ceil(encd)
    else:
        return encd

def main_function():
    # --- Initial values
    l_encd = 0
    r_encd = 0
    l_pwm = None
    r_pwm = None
    head = 180
    f_uss = 10
    r_uss = 10
    l_uss = 10
    last_time_nano_send = 0
    last_time_elegoo_send = 0

    # --- Parse out yaml and set up RX and TX Sockets
    print("Set up ports")
    parsed_out_yml   = dmm.parse_yaml(yaml_file_name)
    interval_list    = yd.intervals_read_send(parsed_out_yml)
    nano_interval_send = interval_list["nano_send_interval"]
    elegoo_interval_send = interval_list["elegoo_send_interval"]
    read_sock_list   = yd.sim_read(parsed_out_yml, ip_setting)
    tx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tx_sendpoints = yd.send_ports(parsed_out_yml, ip_setting)
    time.sleep(0.3)
    
    print("Begin Loop")
    time.sleep(0.3)
    while True:
        now = time.monotonic()
        # --- Read Socket for Elegoo CMD
        read_port, _, _ = select.select(read_sock_list, [], [], 0.02) # 20 ms timeout
        for s in read_port:
            last_pkt = None
            while True:
                try:
                    data_rcv, addr = s.recvfrom(2048)
                except BlockingIOError:
                    break
                last_pkt = data_rcv

            if last_pkt is None:
                continue

            # Convert data into JSON
            data_to_json = json.loads(last_pkt)
            src = dmm.json_reader(data_to_json)

            if src == "mtr_cmd":
                l_dir, r_dir, l_pwm, r_pwm = dmm.sim_mtr_cmd_parser(data_to_json)
                l_encd = l_encd_math(l_pwm, l_encd)
                r_encd = r_encd_math(r_pwm, r_encd)

        #  --- TX Data
        # Elegoo Motor Output
        if now - last_time_elegoo_send > elegoo_interval_send:
            cur_time = time.time()
            elegoo_json = { "source": "elegoo", "R_motor": r_pwm, "L_motor": l_pwm}
            tx_elegoo_json = dmm.json_convert(elegoo_json)
            tx_socket.sendto(tx_elegoo_json, (tx_sendpoints["elegoo"][0], tx_sendpoints["elegoo"][1]))
            last_time_elegoo_send = now
            delta_time = time.time()
            #print(tx_elegoo_json)
            #print(delta_time - cur_time)

        # Nano = USS | Magnemeter | Encoder
        if now - last_time_nano_send > nano_interval_send:
            nano_json = { "source": "nano", 
                            "F_USS": f_uss, "R_USS": r_uss, "L_USS": l_uss,
                            "HEAD": head,
                            "L_ENCD": l_encd, "R_ENCD": r_encd}
            tx_nano_json = dmm.json_convert(nano_json)
            tx_socket.sendto(tx_nano_json, (tx_sendpoints["nano"][0], tx_sendpoints["nano"][1]))
            last_time_nano_send = now
            #print(tx_nano_json)
        time.sleep(0.001)

if __name__ == "__main__":
    main_function()