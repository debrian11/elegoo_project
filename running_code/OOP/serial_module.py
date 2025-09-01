#!/usr/bin/env python3
# pylint: disable=C0114,C0115,C0116,C0301,C0303,C0304
import os
import json
import time
import serial

class SerialPort:
    """ Wrapper around pyserial with JSON helpers and parser
    usb_path : str
        Device path, e.g. '/dev/arduino_nano' or '/dev/ttyUSB0'.

    baud : int
        Baud rate (default 115200).

    serial_timeout : float
        Read timeout in seconds (default 1.0).

    json_parser : callable or None
        Optional function that converts a raw JSON *string* into whatever
        object you want (e.g., NanoPacket). Signature:
            parser(line: str) -> object_or_None
        If not provided, we return a plain dict from json.loads().

    wait_for_device : bool
        If True, block until the device path exists and opens cleanly.
        If False, try once and raise on failure.

    serial_open_delay_s : float
        Delay after opening to allow Arduino auto reset to finish and
        then flush the input buffer.
    """
    def __init__(
        self,
        usb_path: str,
        baudrate: int = 115200,
        serial_timeout: float = 1.0,
        json_parser = None,
        wait_for_device: bool = True,
        serial_open_delay_s: float = 2.0):

        self.usb_path = usb_path
        self.baudrate = baudrate
        self.serial_timeout = serial_timeout
        self.json_parser = json_parser
        self.serial_port = None

        # Wait loop
        if wait_for_device:
            while True: # wait for device node to exist
                if not os.path.exists(self.usb_path):
                    print(f"[SEIAL] {self.usb_path} not present. Retrying....")
                    time.sleep(1.0)
                    continue
                try:
                    self.open_port(serial_open_delay_s)
                    break
                except (serial.SerialException, OSError) as exc:
                    print(f"[SERIAL] Open failed for {self.usb_path}: {exc}. Retrying...")
        else:
            # Try to open the port only once.
            # This is mainly for automated tests so they fail fast
            # if hardware is not connected, instead of hanging forever.
            self.open_port(serial_open_delay_s)

# ------- Open / Close helpers --------- #
    def open_port(self, serial_open_delay_s: float):
        """Open serial port and allow MCU reset time"""
        self.serial_port = serial.Serial(self.usb_path, self.baudrate, timeout = self.serial_timeout)
        time.sleep(serial_open_delay_s) # allow arduino to reset at connection
        self.serial_port.reset_input_buffer() # clear out the the serial port at start

    def try_reopen(self, backoff_s: float = 0.5):
        """ Attempt to reopen once after an error
            Returns True if the port is open again, False otherwise
        """
        try:
            if self.serial_port:
                self.serial_port.close()
        except Exception:
            pass
        try:
            self.open_port(serial_open_delay_s = 0.5)
            print(f"[SERIAL] Reconnected at {self.usb_path}")
            return True
        except Exception as exc:
            print(f"[SERIAL] Reconnect failed {self.usb_path}: {exc}")
            time.sleep(backoff_s)
            return False

# ---Core read path --- #
    def read_json_line(self):
        """Read one line without trailing new line
                Read one text line (UTF 8), stripping the trailing newline.
        Returns:
            str  -> a non-empty line
            None -> on timeout or empty read"""
        if not self.serial_port:
            return False
        try:
            raw_json = self.serial_port.readline().decode("utf-8", errors="ignore").strip()
            return raw_json if raw_json else None
        except (serial.SerialException, OSError):
            if self.try_reopen():
                return None
            return None
        
    def read_json(self):
        """
        Read one JSON message.

        Behavior:
        - If a parser was supplied at construction, pass the *raw string*
          to that parser and return its result (e.g., NanoPacket or None).
        - Otherwise, return a dict from json.loads(line).
        - On timeout / bad JSON / parser failure, return None.

        Returns:
            object | dict | None
        """
        json_line = self.read_json_line()
        if not json_line:
            return None
        
        if self.json_parser is not None:
            return self.json_parser(json_line)
        
        try:
            return json.loads(json_line)
        except json.JSONDecodeError:
            return None
        
# ---Core write path --- #
    def write_json(self, pi_to_elegoo_json):
        """
        Send one JSON message.

        Accepts:
        - dict:        we json.dumps() it
        - str (JSON):  we send as-is
        - object with .send_to_elegoo(): we call it (your MotorCommand)

        Returns:
            True  on apparent success
            False if not sent (type mismatch or write error)
        """
        if not self.serial_port:
            return False
        
        try:
            if isinstance(pi_to_elegoo_json, dict):
                pi_to_elegoo_json = json.dumps(pi_to_elegoo_json)

            if not isinstance(pi_to_elegoo_json, str):
                # Nothing to send. unexpected type
                return False
            
            #Append newline so the arduino readline() side is happy
            self.serial_port.write((pi_to_elegoo_json + "\n").encode("utf-8"))
            return True
        
        except (serial.SerialException, OSError):
            return self.try_reopen()
        