import time
# All test jsons here for Pi to send to entities
# Nano TM to Mac
# Elegoo TM to Mac
# Pi to Mac position data
# Pi to Pi2 cmds
# Elegoo motor cmds


# fwd the sensors to the Mac
def nano_to_mac(counter):
    json_data = {
    "source": "sensors",
    "mssg_id": counter ,
    "HEAD": counter + 5,
    "F_USS": counter + 5,
    "L_USS": counter + 5,
    "R_USS": counter + 5,
    "L_ENCD": counter + 5,
    "R_ENCD": counter + 5
    }
    return json_data

# fwd the motor to the Mac
def elegoo_to_mac(counter):
    json_data = {
    "source": "motor",
    "mssg_id": counter ,
    "L_motor": counter + 3,
    "R_motor": counter + 3
    }
    return json_data

# Send x,y to the Mac
def pi_to_mac_position(counter):
    json_data = {
    "source": "position",
    "time": time.time(),
    "mssg_id": counter ,
    "x_coord": counter,
    "y_coord": counter
    }
    return json_data

# Motor cmds - will need to convert the dir and pwr and send accordingly to the Motors
def pi_to_motor(counter, cmd: str, pwr: int):
    json_data = {
    "source": "motor_cmds",
    "mssg_id": counter ,
    "L_MOTOR": counter,
    "R_MOTOR": counter,
    "L_DIR": counter,
    "R_DIR": counter,
    }
    return json_data

if __name__ == "__main__":
    print(nano_to_mac(1))
    print(elegoo_to_mac(1))
    print(pi_to_mac_position(1))
    print(pi_to_motor(1, "fwd", 100))