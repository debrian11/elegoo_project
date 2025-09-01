#!/usr/bin/env python3
#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304,R0902
""" 
1. record_non_turn(cmd) - save as last non-turn cmd
2. update_uss(uss_dict) - device to turn, keep turning, or resume last cmd
"""

import json
import time

STOP_CMD = {"L_DIR":1, "R_DIR":1, "L_PWM":0, "R_PWM":0}
LEFT_TURN = {"L_DIR":0, "R_DIR":1, "L_PWM":65, "R_PWM":65}
RIGHT_TURN = {"L_DIR":1, "R_DIR":0, "L_PWM":65, "R_PWM":65}

class USSController:
    def __init__(self, turn_threshold = 5, min_turn_s = 0.1, max_turn_s = 0.7, clear_threshold = 2):
        # Turn Thresholds
        self.turn_threshold = turn_threshold
        self.min_turn_s = min_turn_s
        self.max_turn_s = max_turn_s
        self.clear_threshold = clear_threshold

        # State
        self.turning = False
        self.turn_start_time = 0.0
        self.last_non_turn_json = json.dumps(STOP_CMD)

        # Turn cmds
        self.left_turn = json.dumps(LEFT_TURN)
        self.right_turn = json.dumps(RIGHT_TURN)

    def record_non_turn(self, cmd):
        """ Save the last non-turn cmd to resume after turn"""
        if isinstance(cmd, dict):
            self.last_non_turn_json = json.dumps(cmd)
        elif isinstance(cmd, str) and cmd.strip():
            self.last_non_turn_json = cmd.strip()


    def update_uss(self, uss):
        """
        Decide whether to:
        - Start a turn (returns LEFT or RIGHT cmd)
        - Keep turning (Returns None)
        - Resume last cmd after turn (returns that last non-turn cmd)
        - Do nothing (Returns None)
        """

        current_time = time.time()
        try:
            front_data = int(uss.get("F_USS"))
            left_data = int(uss.get("L_USS"))
            right_data = int(uss.get("R_USS"))
        except (TypeError, ValueError):
            return None # invalid data
        
        # Currently turning
        if self.turning:
            elapsed_time = current_time - self.turn_start_time

            if elapsed_time >= self.min_turn_s and all(uss_read > self.clear_threshold for uss_read in (front_data, left_data, right_data)):
                self.turning = False
                return self.last_non_turn_json
            
            if elapsed_time >= self.max_turn_s:
                self.turning = False
                return self.last_non_turn_json
            return None

        # Not currently turning, check for obstacles
        if 0 <= front_data < self.turn_threshold:
            self.turning = True
            self.turn_start_time = current_time
            return self.left_turn if left_data > right_data else self.right_turn
        
        if 0 <= left_data < self.turn_threshold:
            self.turning = True
            self.turn_start_time = current_time
            print("Turn Right")
            return self.right_turn
        
        if 0 <= right_data < self.turn_threshold:
            self.turning = True
            self.turn_start_time = current_time
            print("Turn Left")
            return self.left_turn
        
        return None # Nothing to do
        
