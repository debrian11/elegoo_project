#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304
import socket

def assign_read_sockets(parsed_out_yaml: dict, test_setting: int) -> list:
    all_sockets = {}
    if test_setting == 1:
        rx_ip = "192.168.1.97" # pi ip
    else:
        rx_ip = "192.168.1.72" # laptop ip
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


def intervals_read_send(parsed_out_yaml: dict) -> dict:
    interval_list = {
    "nano_read_interval"        :        parsed_out_yaml["intervals"]["nano_read"],
    "elegoo_read_interval"      :        parsed_out_yaml["intervals"]["elegoo_read"],
    "mac_cmd_read_interval"     :        parsed_out_yaml["intervals"]["mac_cmd_read"],
    "mac_pulse_read_interval"   :        parsed_out_yaml["intervals"]["mac_pulse_read"],
    "pi2_pulse_read"            :        parsed_out_yaml["intervals"]["pi2_pulse_read"],

    "nano_send_interval"        :        parsed_out_yaml["intervals"]["nano_send"],
    "elegoo_send_interval"      :        parsed_out_yaml["intervals"]["elegoo_send"],
    "pi_position_interval"      :        parsed_out_yaml["intervals"]["pi_position"],
    "motor_cmd_interval"        :        parsed_out_yaml["intervals"]["motor_cmd"],
    "pi2_cmd_interval"          :        parsed_out_yaml["intervals"]["pi2_cmd"],

    "f_uss_threshold"           :        parsed_out_yaml["intervals"]["f_uss_threshold"],
    "l_uss_threshold"           :        parsed_out_yaml["intervals"]["l_uss_threshold"],
    "r_uss_threshold"           :        parsed_out_yaml["intervals"]["r_uss_threshold"],
    "turn_time_threshold"       :        parsed_out_yaml["intervals"]["turning_time_threshold"],

    "mac_hb_timeout"            :        parsed_out_yaml["intervals"]["mac_hb_timeout_interval"],
    "mac_cmd_timeout"           :        parsed_out_yaml["intervals"]["mac_cmd_timeout_interval"],
    "pi2_hb_timeout"            :        parsed_out_yaml["intervals"]["pi2_hb_timeout_interval"]
    }
    return interval_list

def send_ports(parsed_out_yaml: dict, test_setting: int) -> dict:
    if test_setting == 1:
        tx_ip = "192.168.1.97" # pi ip
    else:
        tx_ip = "192.168.1.72" # laptop ip

    sendpoints = {
        "nano"      : (tx_ip, parsed_out_yaml["network"]["endpoints"]["nano_to_pi"]["port"]),
        "elegoo"    : (tx_ip, parsed_out_yaml["network"]["endpoints"]["elegoo_to_pi"]["port"]),
        "mac_cmd"   : (tx_ip, parsed_out_yaml["network"]["endpoints"]["mac_cmd"]["port"]),
        "mac_pulse" : (tx_ip, parsed_out_yaml["network"]["endpoints"]["mac_pulse"]["port"]),
        "pi2_pulse" : (tx_ip, parsed_out_yaml["network"]["endpoints"]["pi2_pulse"]["port"])
    } 
    return sendpoints

def send_json(send_socket: socket, cur_time: float, last_time: float, timing_interval: float, send_ip: str, send_port: int, json_msg: str, counter: int, who_sent: str):
    if cur_time - last_time > timing_interval:
        send_socket.sendto(json_msg, (send_ip, send_port))
        last_time = cur_time
        counter += 1
        print(who_sent, json_msg)
    return last_time, counter
