import socket
import select
import json

rx_ip = "192.168.0.21"
sim_motor_info = [rx_ip, 5008]

endpoints = {
    "sim":     (sim_motor_info[0], sim_motor_info[1]),
}

def myfunction(endpoints: dict):
    counter = 0

    # Intialize READ sockets
    all_sockets = {}
    for name, (ip_address, port_used) in endpoints.items():
        read_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        read_socket.bind((ip_address, port_used))
        all_sockets[name] = read_socket
    sock_list = list(all_sockets.values())

    while True:
        counter += 1
        read_ports, _, _ = select.select(sock_list, [], [])

        # Read the ports and store values
        for s in read_ports:
            data, addr = s.recvfrom(2048)   # Data comes in as string
            data_to_json = json.loads(data) # Convert string to json        
            print(counter, data_to_json)

if __name__ == "__main__":
    myfunction(endpoints)