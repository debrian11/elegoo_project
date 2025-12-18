import socket
import select
import json
import time
import data_mgr_module
import data_responder_module as drm

yaml_file_name = 'pi_config.yml'

def assign_read_sockets(parsed_out_yaml: dict) -> list:
    all_sockets = {}
    rx_ip = parsed_out_yaml["network"]["rx_ip"]
    endpoints = {
        "nano"      : (rx_ip, parsed_out_yaml["network"]["endpoints"]["nano_to_pi"]["port"]),
        "elegoo"    : (rx_ip, parsed_out_yaml["network"]["endpoints"]["elegoo_to_pi"]["port"]),
        "mac_cmd"   : (rx_ip, parsed_out_yaml["network"]["endpoints"]["mac_cmd"]["port"]),
        "mac_pulse" : (rx_ip, parsed_out_yaml["network"]["endpoints"]["mac_pulse"]["port"]),
        "pi2_pulse" : (rx_ip, parsed_out_yaml["network"]["endpoints"]["pi2_pulse"]["port"])
    } 

    # Create read sockets for each port
    for name, (ip, port) in endpoints.items():
        read_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        read_socket.bind((ip, port))
        read_socket.setblocking(False)
        all_sockets[name] = read_socket
    sock_list = list(all_sockets.values())
    return sock_list

def myfunction():
    f_uss, r_uss, l_uss, head, l_encd, r_encd, l_motor, r_motor, cmd, pwr, mac_pulse_mssg_id, mac_pulse_time_rvd, pi2_pulse_mssg_id, pi2_pulse_time_rvd = data_mgr_module.initial_values()
    counter = 0
    last_print_time = 0

    # Parse the yaml
    parsed_out_yaml = data_mgr_module.parse_yaml(yaml_file_name)
    interval_list = data_mgr_module.intervals_read_send(parsed_out_yaml)

    # Intialize RX and TX sockets
    sock_list = assign_read_sockets(parsed_out_yaml)
    tx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
            src = data_mgr_module.json_reader(data_to_json)

            if src == "nano":
                old_nano_data = data_to_json
                f_uss, r_uss, l_uss, head, l_encd, r_encd = data_mgr_module.nano_parser(data_to_json)
                print("NANO RXd", counter, data_to_json)

            if src == "elegoo":
                old_elegoo_data = data_to_json
                data_mgr_module.elegoo_parser(data_to_json)
                print("ELEGOO RXd", counter, data_to_json)

            if src == "mac_cmd":
                old_mac_data = data_to_json
                cmd, pwr = data_mgr_module.mac_parser(data_to_json)
                print("MAC CMD", counter, data_to_json)

            if src == "mac_pulse":
                old_mac_data = data_to_json
                mac_pulse_time_rvd, mac_pulse_mssg_id = data_mgr_module.read_mac_heartbeat(data_to_json)
                print("MAC PULSE", counter, data_to_json)
        
            if src == "pi2_pulse":
                old_mac_data = data_to_json
                pi2_pulse_mssg_id, pi2_pulse_time_rvd = data_mgr_module.read_pi2_heartbeat(data_to_json)
                print("PI2", counter, data_to_json)
        
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