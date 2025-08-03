def react_to_left_obstacle(pi_elegoo_port, current_time, last_cmd_sent, right_turn_json):
    print("[USS]: LEFT OBSTACLE: TURN RIGHT")
    pi_elegoo_port.write((json.dumps(right_turn_json) + '\n').encode('utf-8'))
    last_cmd_sent = json.dumps(right_turn_json)
    turning = True
    turn_start_time = current_time
    return last_cmd_sent, turning, turn_start_time


# Replace this block
elif 0 <= L_USS < TURN_THRESHOLD:
    print("[USS]: LEFT OBSTACLE: TURN RIGHT")
    PI_ELEGOO_PORT.write((json.dumps(RIGHT_TURN) + '\n').encode('utf-8'))
    LAST_CMD_SENT_TO_ELEGO = json.dumps(RIGHT_TURN)
    LAST_CMD_TIME = CURRENT_TIME
    TURNING = True
    TURN_START_TIME = CURRENT_TIME

# With this
LAST_CMD_SENT_TO_ELEGO, TURNING, TURN_START_TIME = react_to_left_obstacle(
    PI_ELEGOO_PORT, CURRENT_TIME, LAST_CMD_SENT_TO_ELEGO, RIGHT_TURN
)
LAST_CMD_TIME = CURRENT_TIME
