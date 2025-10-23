#!/usr/bin/env python3
#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304

# Baseline from pi_serial_json 6.0.0.0
# 8/10/2025:
# Refactor into OOP code
# Add heading adjustemtn

import time
import json
import os
import csv
from pi_stream_video_usb import pi_video_stream
from parsing_modules import NanoPacket, ElegooPacket
from network_module import MacClient
from serial_module import SerialPort
from uss_functions import USSController
from heading_module import HeadingHold

os.makedirs("csv_files", exist_ok=True)
log_path = time.strftime("csv_files/nano_log_%Y%m%d_%H%M%S.csv")
new_file = not os.path.exists(log_path) or os.path.getsize(log_path) == 0
csv_log_file = open(log_path, "a", newline="") #"a" = append
csv_writer = csv.writer(csv_log_file) # Create writer object tied to that file
if new_file:
    csv_writer.writerow(["timestamp","F_USS","L_USS","R_USS","L_ENCD","R_ENCD","L_ENCD_COV","R_ENCD_COV","HEAD"])

print("Starting PI_SERIAL stuff shortly!!")
time.sleep(2)

# ----- Global Variables ---- #
STOP_JSON = {"L_DIR": 1, "R_DIR": 1, "L_PWM": 0, "R_PWM": 0}
LAST_CMD_SENT_TO_ELEGO = json.dumps(STOP_JSON)
LAST_CMD_TIME = 0.0
CMD_ELEGOO_RESEND_INTERVAL = 0.2  # seconds
START_TIME = time.time()
START_TIME_DELAY = 5  # seconds to skip initial noisy sensor readings
mac_connected = False 
heading_hold = HeadingHold(kp = 1.0, deadband_deg = 2.0, max_trim = 40) # Create magnometer object
LAST_NON_TURN_CMD = None

# ====================== SERIAL SETUP ==============================================================================================================
ELEGOO_PORT = '/dev/arduino_elegoo'
NANO_PORT = '/dev/arduino_nano'
PI_ELEGOO_PORT = SerialPort(usb_path= ELEGOO_PORT, json_parser = ElegooPacket.parse_elegoo_json)
PI_ELEGOO_PORT.write_json(STOP_JSON)
PI_NANO_PORT = SerialPort(usb_path = NANO_PORT, json_parser = NanoPacket.parsed_nano_json)

# ====================== USS Setup ==============================================================================================================
uss_controller = USSController(turn_threshold = 5, min_turn_s= 0.1, max_turn_s = 0.7, clear_threshold = 8)

# ====================== TCP Setup ==============================================================================================================
mac_host = MacClient(port = 9000)
mac_host.wait_for_connection()
mac_host.attach_elegoo(PI_ELEGOO_PORT)

mac_connected = True
print("Waiting several seconds for Arduino sensors to stabilize...")
time.sleep(2)
# ====================== Start video stream ========================================================================================
camera_usb_path = "/dev/video0"
stream_ip_out = "192.168.0.21"
stream_port_out = 12345
if os.path.exists(camera_usb_path):
    stream_video = pi_video_stream(usb_path=camera_usb_path, ip_out=stream_ip_out, port_out=stream_port_out)
    print(f"Camera connected, starting stream at {stream_ip_out}, port {stream_port_out}")
else:
    print(f"No camera connected at {camera_usb_path}, skipping video stream")

# ====================== LOOP ==============================================================================================================
try:
    while True:
        CURRENT_TIME = time.time()
        # -----------------------------------------NANO to PI----------------------------------------------------
        nano_packet = PI_NANO_PORT.read_json() # serial_module, read_json --> NanoPacket.parsed_nano_json, at this point you have the nano read
        if isinstance(nano_packet, NanoPacket):
            LAST_LINE_NANO_JSON = nano_packet.NANO_RAW
            #qqq 
            print(f"NANO: {nano_packet}")

            # USS decision
            if CURRENT_TIME - START_TIME < START_TIME_DELAY:
                print("Skip initial sensor readings")
            else:
                uss_cmd_send = uss_controller.update_uss({
                    "F_USS": nano_packet.F_USS,
                    "L_USS": nano_packet.L_USS,
                    "R_USS": nano_packet.R_USS
                })
                if mac_connected and uss_cmd_send:
                    PI_ELEGOO_PORT.write_json(uss_cmd_send)
                    LAST_CMD_SENT_TO_ELEGO = uss_cmd_send
                    LAST_CMD_TIME = CURRENT_TIME
                    # Decide: was this a turn command or nah
                    try:
                        cmd = json.loads(uss_cmd_send) if isinstance(uss_cmd_send, str) else uss_cmd_send
                    except Exception:
                        cmd = None

                    if isinstance(cmd, dict) and (cmd.get("L_DIR") != 1 or cmd.get("R_DIR") != 1):
                        # It's a turn command -> disarm HH
                        heading_hold.disarm()
                    else:
                        # change to new heading
                        if isinstance(nano_packet, NanoPacket):
                            heading_hold.arm(nano_packet.HEAD)

            # CSV logging
            csv_writer.writerow([
                time.time(),
                nano_packet.F_USS,
                nano_packet.L_USS,
                nano_packet.R_USS,
                nano_packet.L_ENCD,
                nano_packet.R_ENCD,
                (nano_packet.L_ENCD / 9.4166) if isinstance(nano_packet.L_ENCD, int) else "",
                (nano_packet.R_ENCD / 9.333)  if isinstance(nano_packet.R_ENCD, int) else "",
                nano_packet.HEAD
            ])
            csv_log_file.flush()
            os.fsync(csv_log_file.fileno())

            # Send data to MAC
            mac_host.send_nano_to_mac(nano_packet)

        # -----------------------------------------ELEGOO to PI----------------------------------------------------
        elegoo_packet = PI_ELEGOO_PORT.read_json()
        if isinstance(elegoo_packet, ElegooPacket):
            # qqq
            print(f"ELEGOO: {elegoo_packet}")
            mac_host.send_elegoo_to_mac(elegoo_packet)

        # ------------------------------------------MAC to PI to ELEGOO---------------------------------------------------
        mac_cmd = mac_host.recv_cmd()  # str or None
        corrected = None

        if mac_cmd:
            if not mac_connected:
                print("[MAC] Connection established")
                mac_connected = True
            if mac_host.send_to_elegoo_from_mac(mac_cmd):
                LAST_CMD_SENT_TO_ELEGO = mac_cmd

                # Keep only the last non-empty JSON line, and validate it
                if isinstance(mac_cmd, str):
                    line = mac_cmd.strip().splitlines()[-1] #remove leading/trailing whitespace | split into lines | takes last element (final) of the list
                    # qqq
                    print(f"MAC {line}")
                    try:
                        json.loads(line)  # validate JSON
                        LAST_NON_TURN_CMD = line
                        uss_controller.record_non_turn(line)  # record the cleaned single line
                    except json.JSONDecodeError:
                        # If it isn't valid JSON, do not update LAST_NON_TURN_CMD
                        pass
                else:
                    LAST_NON_TURN_CMD = mac_cmd
                    uss_controller.record_non_turn(mac_cmd)

                LAST_CMD_TIME = CURRENT_TIME
                # Arm heading-hold if this is a straight drive command
                cmd = LAST_NON_TURN_CMD
                if isinstance(cmd, str):
                    cmd = json.loads(cmd)

                if (isinstance(cmd, dict)
                        and cmd.get("L_DIR") == 1 and cmd.get("R_DIR") == 1
                        and cmd.get("L_PWM", 0) > 0 and cmd.get("R_PWM", 0) > 0
                        and isinstance(nano_packet, NanoPacket)):
                    heading_hold.arm(nano_packet.HEAD)
                else:
                    heading_hold.disarm()

        # --- Heading-hold correction runs every loop (only if not turning) ---
        if (not uss_controller.turning
            and LAST_NON_TURN_CMD is not None
            and isinstance(nano_packet, NanoPacket)):

            base = (json.loads(LAST_NON_TURN_CMD)
                    if isinstance(LAST_NON_TURN_CMD, str)
                    else LAST_NON_TURN_CMD)
            
            current_heading = float(nano_packet.HEAD)

            out = heading_hold.process(current_heading, base, turning=uss_controller.turning)

            if out is not base:
                # Optional trace so you SEE the correction
                try:
                    l_trim = out["L_PWM"] - base["L_PWM"]
                    r_trim = out["R_PWM"] - base["R_PWM"]
                    print(f"[HH] target={heading_hold.target:.1f} head={float(nano_packet.HEAD):.1f} "
                        f"trim(L,R)=({l_trim:+d},{r_trim:+d})")
                except Exception:
                    pass

                PI_ELEGOO_PORT.write_json(out)
                LAST_CMD_SENT_TO_ELEGO = out
                LAST_CMD_TIME = CURRENT_TIME

        # --- end heading-hold block ---

        if mac_connected and mac_host.mac_connection is None:
            print("[MAC] Connection lost - sending STOP")
            PI_ELEGOO_PORT.write_json(STOP_JSON)
            LAST_CMD_SENT_TO_ELEGO = STOP_JSON
            LAST_CMD_TIME = CURRENT_TIME
            uss_controller.record_non_turn(STOP_JSON)
            uss_controller.turning = False
            mac_connected = False
            time.sleep(0.5)
            break

        # RESEND LAST CMD TO ARDUINO IF IDLE
        if CURRENT_TIME - LAST_CMD_TIME > CMD_ELEGOO_RESEND_INTERVAL and LAST_CMD_SENT_TO_ELEGO:
            PI_ELEGOO_PORT.write_json(LAST_CMD_SENT_TO_ELEGO)
            LAST_CMD_TIME = CURRENT_TIME

except KeyboardInterrupt:
    print("\nShutting down.")

finally:
    PI_ELEGOO_PORT.serial_port.close()
    PI_NANO_PORT.serial_port.close()
    csv_log_file.close()
    if os.path.exists(f'{camera_usb_path}'):
        stream_video.terminate()
        stream_video.wait()