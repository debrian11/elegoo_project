#!/usr/bin/env python3
#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304
# 8/31/2025 add dataclass
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class HeadingHold:
    kp: float = 1.0
    deadband_deg: float = 3.0
    max_trim: int = 40
    rearm_delay: float = 0.25
    reduce_only: bool = True
    min_trim: int = 0

    active: bool = False
    target: Optional[float] = None
    last_turn_end: float = 0.0
    prev_trim: int = 0


    @staticmethod
    def _is_straight(cmd: dict) -> bool:
        return (cmd.get("L_DIR") == 1 and cmd.get("R_DIR") == 1 and
                cmd.get("L_PWM", 0) > 0 and cmd.get("R_PWM", 0) > 0)

    @staticmethod
    def _clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    @staticmethod
    def _shortest_err_deg(target, head):
        # signed shortest-angle error in degrees, +err = need to yaw right
        e = (target - head + 540.0) % 360.0 - 180.0
        return e

    def arm(self, current_heading: float):
        self.target = float(current_heading)
        self.active = True
        self.prev_trim = 0

    def disarm(self, reason: str = ""):
        self.active = False
        self.target = None
        self.prev_trim = 0

    def apply(self, head_deg: float, base_cmd: dict) -> dict | None:
        """Returns corrected command dict or None if no change."""
        if not self.active or self.target is None:
            return None

        err = self._shortest_err_deg(self.target, head_deg)

        # Deadband: ignore small errors
        if abs(err) <= self.deadband_deg:
            trim = 0
        else:
            trim = self.kp * err
            # clamp magnitude
            trim = self._clamp(trim, -self.max_trim, self.max_trim)
            if self.min_trim and 0 < abs(trim) < self.min_trim:
                trim = self.min_trim if trim > 0 else -self.min_trim

        if trim == 0:
            return None

        baseL = int(base_cmd["L_PWM"]); baseR = int(base_cmd["R_PWM"])
        if trim > 0:
            # +err → yaw right → slow RIGHT wheel only
            l_pwm = baseL
            r_pwm = max(0, baseR - int(trim))
        else:
            # -err → yaw left  → slow LEFT wheel only
            l_pwm = max(0, baseL - int(-trim))
            r_pwm = baseR

        out = dict(base_cmd)
        out["L_PWM"] = self._clamp(l_pwm, 0, 255)
        out["R_PWM"] = self._clamp(r_pwm, 0, 255)
        return out

    def process(self, head_deg: float, base_cmd: dict, turning: bool, now: float | None = None) -> dict:
        """
        Single entry point:
        - Disarms while turning or when not in forward mode.
        - Re-arms after rearm_delay once straight again, targeting current heading.
        - Applies correction if active.
        """
        t = time.monotonic() if now is None else now

        if turning:
            if self.active:
                self.disarm("USS turning")
            self.last_turn_end = t
            return base_cmd

        if not self._is_straight(base_cmd):
            if self.active:
                self.disarm("non-forward cmd")
            return base_cmd

        # Straight and not turning: rearm after a short delay
        if not self.active and (t - self.last_turn_end) >= self.rearm_delay:
            self.arm(head_deg)

        corrected = self.apply(head_deg, base_cmd)
        return corrected or base_cmd
