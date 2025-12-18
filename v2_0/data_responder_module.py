import data_mgr_module as dmm

# Convertdirection cmd'd and pwr into motor json to Arduino
# Expected format for Arduino: { "L_DIR":0, "R_DIR":0, "L_PWM":50, "R_PWM":50 }
def motor_cmd(cmd: str, pwr: int):
    pass

def heading_keeper(head: float): 
    pass

# Defines USS movement logics
def uss_mover(f_uss: int, r_uss: int, l_uss: int):
    pass

def heartbeat_decider(mac_pulse_time_rvd: float, mac_pulse_mssg_id: int):
    pass

def pi2_heartbeat_handler(pi2_pulse_time_rvd: int, pi2_pulse_mssg_id: int):
    pass