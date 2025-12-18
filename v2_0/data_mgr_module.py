import json
import yaml

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
    f_uss =     0
    r_uss =     0
    l_uss =     0
    head =      0
    l_encd =    0
    r_encd =    0

    r_motor =   0
    l_motor =   0

    cmd =       ""
    pwr =       0

    mac_pulse_time_rvd = 0
    mac_pulse_mssg_id = 0
    pi2_pulse_time_rvd = 0
    pi2_pulse_mssg_id = 0

    return f_uss, r_uss, l_uss, head, l_encd, r_encd, l_motor, r_motor, cmd, pwr, mac_pulse_mssg_id, mac_pulse_time_rvd, pi2_pulse_mssg_id, pi2_pulse_time_rvd

# Incoming Nano TM
def nano_parser(json_pkt: dict):
    f_uss = json_pkt.get("F_USS", 0)
    r_uss = json_pkt.get("R_USS", 0)
    l_uss = json_pkt.get("L_USS", 0)
    head = json_pkt.get("HEAD", 0)
    l_encd = json_pkt.get("L_ENCD", 0)
    r_encd = json_pkt.get("R_ENCD", 0)
    return f_uss, r_uss, l_uss, head, l_encd, r_encd

# Incoming Motor TM
def elegoo_parser(json_pkt: dict):
    r_motor = json_pkt.get("R_MOTOR", 0)
    l_motor = json_pkt.get("L_MOTOR", 0)
    return r_motor, l_motor

# Parse out the two values, CMD & PWR, from Mac into useful varaibles (int)
def mac_parser(json_pkt: dict):
    cmd = json_pkt.get("cmd", "N/A")
    pwr = json_pkt.get("speed", 0)
    return cmd, pwr

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
    "pi2_cmd_interval"          :        parsed_out_yaml["intervals"]["pi2_cmd"]
    }
    return interval_list