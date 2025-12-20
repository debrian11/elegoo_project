#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304

# Test tool to send data to the Pi to test the inputs and logics
import socket
import time
import data_mgr_module as dmm   # For parsing out the pi_config.yml
import test_data_sender as tds  # to send data
import yaml_data as yd          # parsed out yaml data for intervals, ports, etc

yaml_file_name = 'pi_config.yml'

def myfunction():
    # parse out yaml
    parsed_out_yaml = dmm.parse_yaml(yaml_file_name)
    interval_list = yd.intervals_read_send(parsed_out_yaml)

    # Port setup
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendpoints = yd.send_ports(parsed_out_yaml)

    # Setup initial time
    lst_t_nano = time.time()
    lst_t_elegoo = time.time()
    lst_t_mac_cmd = time.time()
    lst_t_mac_pulse = time.time()
    lst_t_pi2_pulse = time.time()
    cmd_dir = "fwd"

    # Initial ctrs
    nano_mssg_ctr = 0
    elegoo_msg_ctr = 0
    mac_cmd_msg_ctr = 0
    mac_heart_msg_ctr = 0
    pi2_heart_ctr = 0

    while True:
        current_time = time.time()

        # JSON message generator
        nano_mssg = dmm.json_convert(tds.nano_to_pi(nano_mssg_ctr))
        elegoo_msg = dmm.json_convert(tds.elegoo_to_pi(elegoo_msg_ctr))
        mac_cmd_msg = dmm.json_convert(tds.mac_to_pi(mac_cmd_msg_ctr, cmd_dir))
        mac_heart_msg = dmm.json_convert(tds.mac_heartbeat(mac_heart_msg_ctr))
        pi2_heart_msg = dmm.json_convert(tds.pi2_heartbeat(pi2_heart_ctr))

        # Data send
        lst_t_nano, nano_mssg_ctr    =       yd.send_json(sock, current_time, lst_t_nano,      interval_list["nano_read_interval"],     sendpoints["nano"][0],      sendpoints["nano"][1],      nano_mssg, nano_mssg_ctr,      "nano")
        lst_t_elegoo, elegoo_msg_ctr =       yd.send_json(sock, current_time, lst_t_elegoo,    interval_list["elegoo_read_interval"],   sendpoints["elegoo"][0],    sendpoints["elegoo"][1],    elegoo_msg, elegoo_msg_ctr,    "elegoo")
        lst_t_mac_cmd, mac_cmd_msg_ctr =     yd.send_json(sock, current_time, lst_t_mac_cmd,   interval_list["mac_cmd_read_interval"],  sendpoints["mac_cmd"][0],   sendpoints["mac_cmd"][1],   mac_cmd_msg, mac_cmd_msg_ctr,  "cmd")
        lst_t_mac_pulse, mac_heart_msg_ctr = yd.send_json(sock, current_time, lst_t_mac_pulse, interval_list["mac_pulse_read_interval"],sendpoints["mac_pulse"][0], sendpoints["mac_pulse"][1], mac_heart_msg, mac_heart_msg_ctr, "mac_pulse")
        lst_t_pi2_pulse, pi2_heart_ctr =     yd.send_json(sock, current_time, lst_t_pi2_pulse, interval_list["pi2_pulse_read"],         sendpoints["pi2_pulse"][0], sendpoints["pi2_pulse"][1], pi2_heart_msg, pi2_heart_ctr, "pi2_pulse")

        # Sleep to prevent max speed
        time.sleep(0.001)
    

if __name__ == "__main__":
    myfunction()