#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304, C0411
#This module handles configuring the serial ports for the Arduino's that connect to the Pi.
#  There are two Arduinos.
#  1) Arduino Elegoo = handles motor pwm cmds
#  2) Arduino Nano = handles sensors: Ultrasonic, Encoders, Magnometer 
# Handles the reading / writing to those ports

import serial
import time
import os
import json

# Setting up the serial ports        
def serial_port_setup(port_name: str, baud_rate: int):
    while True:
        if not os.path.exists(port_name):
            print(f"{port_name} not connected, retrying...")
            time.sleep(1.0)
            continue
        elif os.path.exists(port_name):
            serial_port = serial.Serial(port=port_name, baudrate=baud_rate, timeout=0)
            time.sleep(3.0)
            serial_port.reset_input_buffer()
            print(F"Connected to port at {port_name}")
            return serial_port
        
def write_json(serial_port, mtr_cmd: str):
    if isinstance(mtr_cmd, str):
        serial_port.write((mtr_cmd + "\n").encode("utf-8"))

# Reads the line input from the serial ports at each "\n"
# This actually doesn't work because the serial lines don't show up as complete JSONs to parse.
def readline_json(serial_port):
    raw_serial_input = serial_port.readline().decode("utf-8", errors="ignore").strip()
    return raw_serial_input

# This method reads bytes vs a whole line. Reading bytes will be more robust for error handling
def read_json(serial_port, buffer):
    raw_serial_data = serial_port.read(serial_port.in_waiting or 1).decode("utf-8", errors="ignore")

    if raw_serial_data:
        buffer += raw_serial_data

        if "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            try:
                return json.loads(line), buffer
            except json.JSONDecodeError:
                return None, buffer
            
        return None, buffer
    
    return None, buffer
