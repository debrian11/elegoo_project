# Test tool to send data to the Pi to test the inputs and logics
import socket
import time
import data_mgr_module as dmm
import test_data_sender as tds

yaml_file_name = 'pi_config.yml'

def send_ports(parsed_out_yaml: dict) -> dict:
    tx_ip = parsed_out_yaml["network"]["rx_ip"]
    sendpoints = {
        "nano"      : (tx_ip, parsed_out_yaml["network"]["endpoints"]["nano_to_pi"]["port"]),
        "elegoo"    : (tx_ip, parsed_out_yaml["network"]["endpoints"]["elegoo_to_pi"]["port"]),
        "mac_cmd"   : (tx_ip, parsed_out_yaml["network"]["endpoints"]["mac_cmd"]["port"]),
        "mac_pulse" : (tx_ip, parsed_out_yaml["network"]["endpoints"]["mac_pulse"]["port"]),
        "pi2_pulse" : (tx_ip, parsed_out_yaml["network"]["endpoints"]["pi2_pulse"]["port"])
    } 
    return sendpoints

def myfunction():
    counter = 0
    # parse out yaml
    parsed_out_yaml = dmm.parse_yaml(yaml_file_name)
    interval_list = dmm.intervals_read_send(parsed_out_yaml)

    # Port setup
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendpoints = send_ports(parsed_out_yaml)

    # Setup initial time
    last_time_nano = time.time()
    last_time_elegoo = time.time()
    last_time_mac_cmd = time.time()
    cmd_dir = "fwd"


    while True:
        current_time = time.time()

        # JSON message generator
        nano_mssg = dmm.json_convert(tds.nano_to_pi(counter))
        elegoo_msg = dmm.json_convert(tds.elegoo_to_pi(counter))
        mac_cmd_msg = dmm.json_convert(tds.mac_to_pi(counter, cmd_dir))

        # nano send
        if current_time - last_time_nano > interval_list["nano_read_interval"]:
            sock.sendto(nano_mssg, (sendpoints["nano"][0],  sendpoints["nano"][1]))
            last_time_nano = current_time
            counter += 1
            print("nano send", nano_mssg)

        # elegoo send
        if current_time - last_time_elegoo > interval_list["elegoo_read_interval"]:
            sock.sendto(elegoo_msg, (sendpoints["elegoo"][0],    sendpoints["elegoo"][1]))
            last_time_elegoo = current_time
            counter += 1
            print("elegoo send", elegoo_msg)

        # mac send
        if current_time - last_time_mac_cmd > interval_list["mac_cmd_read_interval"]:
            sock.sendto(mac_cmd_msg, (sendpoints["mac_cmd"][0],   sendpoints["mac_cmd"][1]))
            last_time_mac_cmd = current_time
            counter += 1
            print("mac_send", mac_cmd_msg)

if __name__ == "__main__":
    myfunction()