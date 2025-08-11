#!/usr/bin/env python3
#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304

# --- Simple heading hold ---
def _wrap180(deg: float) -> float:
    # Map any angle to (-180, 180]
    d = (deg + 180.0) % 360.0 - 180.0
    return d if d != -180.0 else 180.0

class HeadingHold:
    def __init__(self, kp=0.8, deadband_deg=2.0, max_trim=25, heading_sign=1):
        """
        kp: proportional gain -> PWM trim per degree of error
        deadband_deg: no correction if |error| <= this
        max_trim: clamp trim PWM magnitude
        heading_sign: +1 or -1 depending on your heading convention
                      (set after a quick test)
        """
        self.kp = kp
        self.deadband = deadband_deg
        self.max_trim = max_trim
        self.heading_sign = heading_sign
        self.active = False
        self.target = None   # degrees

    def arm(self, current_heading: float):
        self.target = float(current_heading)
        self.active = True

    def disarm(self):
        self.active = False
        self.target = None

    def apply(self, current_heading: float, base_cmd: dict) -> dict | None:
        """Return corrected cmd or None if no change."""
        if not self.active or self.target is None:
            return None

        try:
            ch = float(current_heading)
        except (TypeError, ValueError):
            return None

        # Only correct straight-line commands (both DIR==1 and both PWM>0)
        if not (isinstance(base_cmd, dict) and
                base_cmd.get("L_DIR") == 1 and base_cmd.get("R_DIR") == 1 and
                base_cmd.get("L_PWM", 0) > 0 and base_cmd.get("R_PWM", 0) > 0):
            return None

        err = _wrap180(self.target - ch)  # desired - current
        if abs(err) <= self.deadband:
            return None

        trim = self.heading_sign * self.kp * err
        # Clamp trim and build corrected PWMs (opposite adjustments)
        trim = max(-self.max_trim, min(self.max_trim, trim))

        l_pwm = int(max(0, base_cmd["L_PWM"] + trim))
        r_pwm = int(max(0, base_cmd["R_PWM"] - trim))

        # If nothing changed meaningfully, skip
        if l_pwm == base_cmd["L_PWM"] and r_pwm == base_cmd["R_PWM"]:
            return None

        corrected = dict(base_cmd)
        corrected["L_PWM"] = l_pwm
        corrected["R_PWM"] = r_pwm
        return corrected
