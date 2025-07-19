def decide_uss_action(f_dist, l_dist, r_dist, turning):
    if f_dist < F_TURN_THRESHOLD:
        if l_dist > r_dist and not turning:
            print("[PI] FRONT OBSTACLE - MORE SPACE LEFT: TURN LEFT")
            return LEFT_TURN, True
        elif r_dist > l_dist and not turning:
            print("[PI] FRONT OBSTACLE - MORE SPACE RIGHT: TURN RIGHT")
            return RIGHT_TURN, True
    elif l_dist < L_TURN_THRESHOLD and not turning:
        print("[PI] LEFT OBSTACLE: TURN RIGHT")
        return RIGHT_TURN, True
    elif r_dist < R_TURN_THRESHOLD and not turning:
        print("[PI] RIGHT OBSTACLE: TURN LEFT")
        return LEFT_TURN, True
    elif turning:
        print("[PI] CLEAR - RESUME LAST COMMAND")
        return LAST_NON_TURN_CMD, False
    return None, turning  # No new action, keep current turning state
