#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304
import json
import yaml


# Module's purpose is to:
# 1) Determine where the receiving JSON came from (i.e, Elegoo, Nano, Laptop, Pi)
# 2) Parse out the JSON with respective parser then assign values in variables


# --- Data formats --- #
# Get the src of the json
def json_reader(json_pkt: dict):
    src = json_pkt.get("source")
    return src

def json_convert(packet: dict):
    packet_serial = json.dumps(packet)
    encoded_packet = packet_serial.encode("utf-8")
    return encoded_packet

# Reads Yaml and return dictionary
def parse_yaml(yaml_file_name: str) -> dict:
    with open(yaml_file_name, 'r') as file:
        read_yaml = yaml.full_load(file)
    return read_yaml

# ------
def initial_values():
    f_uss =     None
    r_uss =     None
    l_uss =     None
    head =      0
    l_encd =    0
    r_encd =    0
    r_motor =   0
    l_motor =   0
    cmd =       "STOP"
    pwr =       0
    return f_uss, r_uss, l_uss, head, l_encd, r_encd, l_motor, r_motor, cmd, pwr

def initial_time_values():
    mac_pulse_time_rvd = 0
    pi2_pulse_time_rvd = 0
    nano_time = 0
    elegoo_time = 0
    mac_cmd_time = 0

    last_mac_cmd_time_rcv = 0
    last_mac_pulse_time_rcv = 0
    last_time_turned = 0
    return mac_pulse_time_rvd, pi2_pulse_time_rvd, nano_time, elegoo_time, mac_cmd_time, last_mac_cmd_time_rcv, last_mac_pulse_time_rcv, last_time_turned

def initial_mssg_id_values():
    mac_pulse_mssg_id = 0
    pi2_pulse_mssg_id = 0
    nano_id = 0
    elegoo_id = 0
    mac_cmd_id = 0
    return mac_pulse_mssg_id, pi2_pulse_mssg_id, nano_id, elegoo_id, mac_cmd_id

# Incoming Nano TM
def nano_parser(json_pkt: dict):
    f_uss = json_pkt.get("F_USS", 0)
    r_uss = json_pkt.get("R_USS", 0)
    l_uss = json_pkt.get("L_USS", 0)
    head = json_pkt.get("HEAD", 0)
    l_encd = json_pkt.get("L_ENCD", 0)
    r_encd = json_pkt.get("R_ENCD", 0)
    nano_time = json_pkt.get("time", 0)
    nano_id = json_pkt.get("mssg_id", 0)
    return f_uss, r_uss, l_uss, head, l_encd, r_encd, nano_time, nano_id

# Incoming Motor TM
def elegoo_parser(json_pkt: dict):
    r_motor = json_pkt.get("R_MOTOR", 0)
    l_motor = json_pkt.get("L_MOTOR", 0)
    elegoo_time = json_pkt.get("time", 0)
    elegoo_id = json_pkt.get("mssg_id", 0)
    return r_motor, l_motor, elegoo_time, elegoo_id

# Parse out the two values, CMD & PWR, from Mac into useful varaibles (int)
def mac_parser(json_pkt: dict):
    cmd = json_pkt.get("cmd", "N/A")
    pwr = json_pkt.get("pwr", 0)
    mac_cmd_time = json_pkt.get("time", 0)
    mac_cmd_id = json_pkt.get("mssg_id", 0)
    return cmd, pwr, mac_cmd_time, mac_cmd_id

# Mac Heartbeat
def read_mac_heartbeat(json_pkt: dict):
    mac_pulse_time_rcv = json_pkt.get("time", 0)
    mac_pulse_mssg_id = json_pkt.get("mssg_id", 0)
    return mac_pulse_time_rcv, mac_pulse_mssg_id

# Pi2 Heartbeat
def read_pi2_heartbeat(json_pkt: dict):
    pi2_pulse_time_rcv = json_pkt.get("time", 0)
    pi2_pulse_mssg_id = json_pkt.get("mssg_id", 0)
    return pi2_pulse_time_rcv, pi2_pulse_mssg_id

# Returns encoded packet after converting JSON (dict) --> Str --> Bytes
def motor_cmder(motor_cmd: dict):
    output = json.dumps(motor_cmd)
    encoded_packet = output.encode("utf-8")
    return encoded_packet
