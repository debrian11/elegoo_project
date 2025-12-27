#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304. C0411

import data_mgr_module as dmm
import yaml_data as yd
import json
import time

all_states = ["FWD", "LEFT", "RIGHT", "BACK", "STOP"]

# Convertdirection cmd'd and pwr into motor json to Arduino
def heading_keeper(head: float, cur_time: float): 
    pass

# Defines USS movement logics
def uss_mover(f_uss: int, r_uss: int, l_uss: int,  cur_time: float):
    pass

def mac_hb_checker(mac_pulse_time_rvd: float, current_time: float, hb_timeout_interval: int) -> bool:
    if isinstance(mac_pulse_time_rvd, float):
        if current_time - mac_pulse_time_rvd > hb_timeout_interval:
            return False
        if current_time - mac_pulse_time_rvd < hb_timeout_interval:
            print(current_time - mac_pulse_time_rvd)
            return True


def pi2_hb_checker(pi2_pulse_time_rvd: int, current_time: float, pi2):
    pass

def cmd_timeout_checker(cmd: str, mac_cmd_time: float, current_time: float, cmd_timeout_interval: int) -> bool:
    if cmd in all_states:
        if current_time - mac_cmd_time > cmd_timeout_interval:
            return False
        else:
            return True
    
def the_state_machine(link_state: str, cur_time: float, mac_pulse_time_rvd: float, mac_pulse_mssg_id: int):
    pass

# Expected format for Arduino: { "L_DIR":0, "R_DIR":0, "L_PWM":50, "R_PWM":50 }
def motor_cmd_UDP(cmd: str, pwr: int) -> str:
    pwr_adjust = 1
    fwd_cmd =   { "L_DIR": 1, "R_DIR": 1, "L_PWM": pwr*(pwr_adjust),        "R_PWM": pwr*(pwr_adjust) }
    left_cmd =  { "L_DIR": 1, "R_DIR": 1, "L_PWM": pwr*(pwr_adjust)*(0.5),  "R_PWM": pwr*(pwr_adjust) }
    right_cmd = { "L_DIR": 1, "R_DIR": 1, "L_PWM": pwr*(pwr_adjust),        "R_PWM": pwr*(pwr_adjust)*(-0.5) }
    back_cmd =  { "L_DIR": 0, "R_DIR": 0, "L_PWM": pwr*(pwr_adjust),         "R_PWM": pwr*(pwr_adjust) }
    stop_cmd =  { "L_DIR": 1, "R_DIR": 1, "L_PWM": 0, "R_PWM": 0 }


    if cmd not in all_states:
        motor_cmd = json.dumps(stop_cmd)

    elif cmd in all_states:
        if cmd == all_states[0]:    # FWD
            motor_cmd = json.dumps(fwd_cmd)

        elif cmd == all_states[1]:  # LEFT
            motor_cmd = json.dumps(left_cmd)

        elif cmd == all_states[2]:  # RIGHT
            motor_cmd = json.dumps(right_cmd)

        elif cmd == all_states[3]:  # BACK
            motor_cmd = json.dumps(back_cmd)

        elif cmd == all_states[4]:  # STOP
            motor_cmd = json.dumps(stop_cmd)

        #print(motor_cmd)
        return motor_cmd
