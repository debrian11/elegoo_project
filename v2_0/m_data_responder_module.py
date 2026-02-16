#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304. C0411
# Module is responsible for:
# 1) Return true or false for the Heartbeat checkers
#    - Mac cmd, Mac hb mssg, Pi hb mssg
# 2) Motor cmds:
#   - Have set values for movement
#   - Check if turning or not
#   - return the converted dictionary into a JSON dumps

import json
import math

all_states = ["FWD", "LEFT", "RIGHT", "BACK", "STOP"]

# Convertdirection cmd'd and pwr into motor json to Arduino
def mac_hb_checker(mac_pulse_time_rvd: float, current_time: float, hb_timeout_interval: int) -> bool:
    if isinstance(mac_pulse_time_rvd, float):
        if current_time - mac_pulse_time_rvd > hb_timeout_interval:
            return False
        elif current_time - mac_pulse_time_rvd < hb_timeout_interval:
            #print(current_time - mac_pulse_time_rvd)
            return True

def pi2_hb_checker(pi2_pulse_time_rvd: int, current_time: float, pi2):
    pass

def cmd_timeout_checker(cmd: str, mac_cmd_time: float, current_time: float, cmd_timeout_interval: int) -> bool:
    if cmd in all_states:
        if current_time - mac_cmd_time > cmd_timeout_interval:
            return False
        else:
            return True

# Expected format for Arduino: { "L_DIR":0, "R_DIR":0, "L_PWM":50, "R_PWM":50 }
def fallback_motor_cmd() -> str:
    stop_cmd =  { "L_DIR": 1, "R_DIR": 1, "L_PWM": 0, "R_PWM": 0 }
    return json.dumps(stop_cmd)        

def heading_keeper(target_heading: int, cur_heading: int): 
    # NEED TO DETERMINE HOW TO LOCK TARGET HEADING
    # NEED TO DETERMINE HOW TO BOUND DEGREES WITHIN 360
    # NEED TO DETERMINE DEAD BAND
    adjust_value = 1.5
    delta_angle = target_heading - cur_heading
    # TBD
    l_mtr_adjust = math.ceil((1)*(delta_angle)*(adjust_value))
    r_mtr_adjust = math.ceil((-1)*(delta_angle)*(adjust_value))
    print("L MTR Adjust = ", l_mtr_adjust, " |  R MTR Adjust = ", r_mtr_adjust)
    return l_mtr_adjust, r_mtr_adjust
    

    
# Expected format for Arduino: { "L_DIR":0, "R_DIR":0, "L_PWM":50, "R_PWM":50 }
def motor_cmd(cmd: str, pwr: int, turning: bool, done_turning: bool, f_uss: int, l_uss: int, r_uss: int, 
              tgt_heading: int, cur_heading: int, last_time_turned: float, cur_time: float, motor_cmd: str,
              f_uss_threshold: int, l_uss_threshold: int, r_uss_threshold: int, turning_time_threshold: float):
    # Heading Adjuster
    #l_mtr_adjust, r_mtr_adjust = heading_keeper(tgt_heading, cur_heading)
    l_mtr_adjust = 0; r_mtr_adjust = 0

    fwd_cmd =   { "L_DIR": 1, "R_DIR": 1, "L_PWM": (pwr - l_mtr_adjust), "R_PWM": (pwr-r_mtr_adjust) }
    left_cmd =  { "L_DIR": 1, "R_DIR": 1, "L_PWM": pwr*(0.5),  "R_PWM": pwr }
    right_cmd = { "L_DIR": 1, "R_DIR": 1, "L_PWM": pwr, "R_PWM": pwr*(0.5) }
    back_cmd =  { "L_DIR": 0, "R_DIR": 0, "L_PWM": pwr, "R_PWM": pwr }
    stop_cmd =  { "L_DIR": 1, "R_DIR": 1, "L_PWM": 0, "R_PWM": 0 }
    
    # comment 1 or 0 to print stuff
    print_stuff = 0

    done_turning = cur_time - last_time_turned
    if done_turning >= turning_time_threshold:
        done_turning = True
        turning = False
    else:
        done_turning = False
        turning = True

    # USS Check
    if f_uss is None or l_uss is None or r_uss is None:
        # USS stuff isn't initialized yet, but allow cmds to run
        if print_stuff == 1:
            print("not Turning", f_uss, l_uss, r_uss, cmd, turning, done_turning, motor_cmd)
        if cmd in all_states:
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
        return motor_cmd, last_time_turned, done_turning, turning

    # If all 3 are not clear
    elif f_uss < f_uss_threshold and l_uss < l_uss_threshold and r_uss < r_uss_threshold:
        if done_turning is True:
            motor_cmd = json.dumps(back_cmd)
            turning = True
            last_time_turned = cur_time
            if print_stuff == 1:
                print("BACK", f_uss, l_uss, r_uss, cmd, turning, done_turning, motor_cmd)
            return motor_cmd, last_time_turned, done_turning, turning
        return motor_cmd, last_time_turned, done_turning, turning
        
    # If Front is not clear
    elif f_uss < f_uss_threshold:
        if l_uss < r_uss:
            if done_turning is True:
                motor_cmd = json.dumps(right_cmd)
                turning = True
                last_time_turned = cur_time
                if print_stuff == 1:
                    print("RIGHT", f_uss, l_uss, r_uss, cmd, turning, done_turning, motor_cmd)
                return motor_cmd, last_time_turned, done_turning, turning
            return motor_cmd, last_time_turned, done_turning, turning

        elif r_uss > l_uss:
            if done_turning is True:
                motor_cmd = json.dumps(left_cmd)
                turning = True
                last_time_turned = cur_time
                if print_stuff == 1:
                    print("LEFT", f_uss, l_uss, r_uss, cmd, turning, done_turning, motor_cmd)
                return motor_cmd, last_time_turned, done_turning, turning
            return motor_cmd, last_time_turned, done_turning, turning
        
        else:
            if done_turning is True:
                motor_cmd = json.dumps(left_cmd)
                turning = True
                last_time_turned = cur_time
                if print_stuff == 1:
                    print("LEFT", f_uss, l_uss, r_uss, cmd, turning, done_turning, motor_cmd)
                return motor_cmd, last_time_turned, done_turning, turning
            return motor_cmd, last_time_turned, done_turning, turning
        
    # If Left is not clear
    elif l_uss < l_uss_threshold:
        if done_turning is True:
            motor_cmd = json.dumps(right_cmd)
            turning = True
            last_time_turned = cur_time
            if print_stuff == 1:
                print("RIGHT", f_uss, l_uss, r_uss, cmd, turning, done_turning, motor_cmd)
            return motor_cmd, last_time_turned, done_turning, turning
        return motor_cmd, last_time_turned, done_turning, turning
    
    # If Right is not clear
    elif r_uss < r_uss_threshold:
        if done_turning is True:
            motor_cmd = json.dumps(left_cmd)
            turning = True
            last_time_turned = cur_time
            if print_stuff == 1:
                print("LEFT", f_uss, l_uss, r_uss, cmd, turning, done_turning, motor_cmd)            
            return motor_cmd, last_time_turned, done_turning, turning
        return motor_cmd, last_time_turned, done_turning, turning
    

    # If all clear on USS and not turning, execute cmd
    elif f_uss > f_uss_threshold and r_uss > r_uss_threshold and l_uss > l_uss_threshold:
        if done_turning is True:
            if print_stuff == 1:
                print("not Turning", f_uss, l_uss, r_uss, cmd, turning, done_turning, motor_cmd)
            if cmd in all_states:
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

            return motor_cmd, last_time_turned, done_turning, turning
        return motor_cmd, last_time_turned, done_turning, turning
    
    