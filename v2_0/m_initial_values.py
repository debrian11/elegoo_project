#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304,C0411

# This module stores the initial values for variables to initialize
def initial_values():
    f_uss =     None
    r_uss =     None
    l_uss =     None
    head =      0
    l_encd =    0
    r_encd =    0
    r_motor =   0
    l_motor =   0
    cmd =       "STOP"
    pwr =       0
    return f_uss, r_uss, l_uss, head, l_encd, r_encd, l_motor, r_motor, cmd, pwr

def initial_time_values():
    mac_pulse_time_rvd = 0
    pi2_pulse_time_rvd = 0
    mac_cmd_time = 0

    last_mac_cmd_time_rcv = 0
    last_mac_pulse_time_rcv = 0
    last_time_turned = 0
    return mac_pulse_time_rvd, pi2_pulse_time_rvd, mac_cmd_time, last_mac_cmd_time_rcv, last_mac_pulse_time_rcv, last_time_turned

def initial_mssg_id_values():
    mac_pulse_mssg_id = 0
    pi2_pulse_mssg_id = 0
    nano_id = 0
    elegoo_id = 0
    mac_cmd_id = 0
    return mac_pulse_mssg_id, pi2_pulse_mssg_id, nano_id, elegoo_id, mac_cmd_id

def intial_boolean_values():
    link_checker =   False
    new_cmd =        False
    turning =        False
    done_turning =   False
    return link_checker, new_cmd, turning, done_turning
