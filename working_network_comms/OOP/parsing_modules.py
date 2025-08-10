#!/usr/bin/env python3
# pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304

""" Modules file for the pi_serial_json classes and methods
Parses outdata for sensor (Nano) and motor (Elegoo)
"""
import json
from dataclasses import dataclass
from typing import Any, Dict

# ---------------- Nano (Sensor) data ------------------- #
# {"mssg_id":993,"F_USS":12,"L_USS":16,"R_USS":89,"L_ENCD":315,"R_ENCD":52}
@dataclass
class NanoPacket:
    """ Sensor data from Arduino Nano"""
    NANO_MSSG_ID: Any
    HEAD: Any
    F_USS: Any
    L_USS: Any
    R_USS: Any
    L_ENCD: Any
    R_ENCD: Any
    NANO_RAW: str

    def is_valid(self):
        """ Check if USS data is valid int"""
        USS_INT_CHECK = [self.F_USS, self.L_USS, self.R_USS]
        for x in USS_INT_CHECK:
            if not isinstance(x, int):
                return False
        return True
    
    @classmethod
    def parsed_nano_json(cls, json_data: str):
        """ Parse out the JSON string into into the NanoPacket"""
        try:
            parsed_json: Dict[str, Any] = json.loads(json_data)
        except json.JSONDecodeError:
            return None
        return cls(
            NANO_MSSG_ID = parsed_json.get("mssg_id", "N/A"),
            HEAD = parsed_json.get("HEAD", "N/A"),
            F_USS= parsed_json.get("F_USS", "N/A"),
            L_USS = parsed_json.get("L_USS", "N/A"),
            R_USS = parsed_json.get("R_USS", "N/A"),
            L_ENCD = parsed_json.get("L_ENCD", "N/A"),
            R_ENCD = parsed_json.get("R_ENCD", "N/A"),
            NANO_RAW = json_data)

# ---------------- Elegoo (Motor) data ------------------- #
# {"mssg_id":106,"L_motor":0,"R_motor":0}
@dataclass
class ElegooPacket:
    """ Motor data from Arduino Elegoo"""
    ELEGOO_MSSG_ID: Any
    L_MTR_DATA: Any
    R_MTR_DATA: Any
    ELEGOO_RAW: str

    def is_valid(self):
        """ Check if motor data is valid int"""
        MTR_CHECK = [self.L_MTR_DATA, self.R_MTR_DATA]
        for y in MTR_CHECK:
            if not isinstance(y, int):
                return False
        return True
    
    @classmethod
    def parse_elegoo_json(cls, json_data: str):
        """Parse out the JSON string into ElegooPacket"""
        try:
            parsed_json: Dict[str, Any] = json.loads(json_data)
        except json.JSONDecodeError:
            return None
        return cls(
            ELEGOO_MSSG_ID = parsed_json.get("mssg_id", "N/A"),
            L_MTR_DATA = parsed_json.get("L_motor", "N/A"),
            R_MTR_DATA= parsed_json.get("R_motor", "N/A"),
            ELEGOO_RAW = json_data)


@dataclass
class MotorCommand:
    L_PWM: int
    R_PWM: int
    L_DIR: int
    R_DIR: int

    def send_to_elegoo(self):
        return json.dumps({
            "L_PWM": self.L_PWM, "R_PWM": self.R_PWM,
            "L_DIR": self.L_DIR, "R_DIR": self.R_DIR
        })