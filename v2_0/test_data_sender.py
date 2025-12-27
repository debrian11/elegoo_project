import time
# All test jsons here to send to the Pi
# Nano
# Elegoo
# Mac Cmds
# Mac Heartbeat
# Pi2 Heartbeat


# USS sensor | Encoders | Magnometer incoming
def nano_to_pi(counter):
    json_data = {
    "source": "nano",
    "time": time.time(),
    "mssg_id": counter ,
    "HEAD": counter,
    "F_USS": counter + 5,
    "L_USS": counter + 5,
    "R_USS": counter + 5,
    "L_ENCD": counter + 5,
    "R_ENCD": counter + 5
    }
    return json_data

# Motor incoming
def elegoo_to_pi(counter):
    json_data = {
    "source": "elegoo",
    "time": time.time(),
    "mssg_id": counter ,
    "L_MOTOR": counter + 3,
    "R_MOTOR": counter + 3
    }
    return json_data

# Mac CMD incoming
def mac_to_pi(counter, random_dir):
    json_data = {
    "source": "mac_cmd",
    "time": time.time(),
    "mssg_id": counter ,
    "cmd": random_dir,
    "pwr": 100
    }
    return json_data

# Mac Heartbeat incoming
def mac_heartbeat(counter):
    json_data = {
    "source": "mac_pulse",
    "time": time.time(),
    "mssg_id": counter ,
    "pulse": "qqq"
    }
    return json_data


# Pi2 Heartbeat incoming
def pi2_heartbeat(counter):
    json_data = {
    "source": "pi2_pulse",
    "time": time.time(),
    "mssg_id": counter ,
    "pulse": "qqq"
    }
    return json_data

if __name__ == "__main__":
    print(nano_to_pi(1))
    print(elegoo_to_pi(2))
    print(mac_to_pi(1, "fwd"))
    print(mac_heartbeat(5))



