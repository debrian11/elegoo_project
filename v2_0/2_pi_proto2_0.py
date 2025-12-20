#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304
import socket
import select
import json
import time
import data_mgr_module as data_mgr
import data_responder_module as drm
import yaml_data as yd

yaml_file_name = 'pi_config.yml'

def myfunction():
    f_uss, r_uss, l_uss, head, l_encd, r_encd, l_motor, r_motor, cmd, pwr, mac_pulse_mssg_id, mac_pulse_time_rvd, pi2_pulse_mssg_id, pi2_pulse_time_rvd = data_mgr.initial_values()
    counter = 0

    # Parse the yaml
    parsed_out_yaml = data_mgr.parse_yaml(yaml_file_name)
    interval_list = yd.intervals_read_send(parsed_out_yaml)

    # Intialize RX and TX sockets
    sock_list = yd.assign_read_sockets(parsed_out_yaml)
    tx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # --- Read the data ---
    # Initialize TX Socket
    while True:
        current_time = time.time()
        counter += 1
        read_ports, _, _ = select.select(sock_list, [], [], 0.02) # 20 ms timeout

        # Read the ports and store values
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
                f_uss, r_uss, l_uss, head, l_encd, r_encd = data_mgr.nano_parser(data_to_json)
                print("NANO RXd", counter, data_to_json)

            if src == "elegoo":
                data_mgr.elegoo_parser(data_to_json)
                print("ELEGOO RXd", counter, data_to_json)

            if src == "mac_cmd":
                cmd, pwr = data_mgr.mac_parser(data_to_json)
                print("MAC CMD", counter, data_to_json)

            if src == "mac_pulse":
                mac_pulse_time_rvd, mac_pulse_mssg_id = data_mgr.read_mac_heartbeat(data_to_json)
                print("MAC PULSE", counter, data_to_json)
        
            if src == "pi2_pulse":
                pi2_pulse_mssg_id, pi2_pulse_time_rvd = data_mgr.read_pi2_heartbeat(data_to_json)
                print("PI2_pulse", counter, data_to_json)
        
        # --- React based on data --- #
        # Mac heartbeat decider
        drm.heartbeat_decider(mac_pulse_time_rvd, mac_pulse_mssg_id)

        # Pi2 heartbeat decider
        drm.pi2_heartbeat_handler(pi2_pulse_time_rvd, pi2_pulse_mssg_id)

        # USS react
        drm.uss_mover(f_uss, r_uss, l_uss)

        # Movement
        drm.motor_cmd(cmd, pwr)

        # Heading keeper
        drm.heading_keeper(head)

if __name__ == "__main__":
    myfunction()