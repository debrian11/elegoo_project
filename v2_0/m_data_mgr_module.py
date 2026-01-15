#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304,C0411
import json
import yaml
import serial
import time
import os
import csv

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

# Incoming Nano TM
def nano_parser(json_pkt: dict):
    f_uss = json_pkt.get("F_USS", 0)
    r_uss = json_pkt.get("R_USS", 0)
    l_uss = json_pkt.get("L_USS", 0)
    head = json_pkt.get("HEAD", 0)
    l_encd = json_pkt.get("L_ENCD", 0)
    r_encd = json_pkt.get("R_ENCD", 0)
    nano_id = json_pkt.get("mssg_id", 0)
    return f_uss, r_uss, l_uss, head, l_encd, r_encd, nano_id

# Incoming Motor TM
def elegoo_parser(json_pkt: dict):
    r_motor = json_pkt.get("R_motor", 0)
    l_motor = json_pkt.get("L_motor", 0)
    elegoo_id = json_pkt.get("mssg_id", 0)
    return r_motor, l_motor, elegoo_id

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

def csv_logger(log_path: str):
    os.makedirs("csv_files", exist_ok=True)
    new_file = not os.path.exists(log_path) or os.path.getsize(log_path) == 0
    csv_log_file = open(log_path, "a", newline="") #"a" = append
    csv_writer = csv.writer(csv_log_file) # Create writer object tied to that file
    if new_file:
        csv_writer.writerow(["timestamp","F_USS","L_USS","R_USS","L_ENCD","R_ENCD","L_ENCD_COV","R_ENCD_COV","HEAD"])
    return csv_writer

