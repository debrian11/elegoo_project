#!/usr/bin/env python3
# pylint: disable=C0114,C0115,C0116,C0301,C0303,C0304

#import os
from __future__ import annotations
import json
import time
import socket
from collections import OrderedDict
from parsing_modules import ElegooPacket, NanoPacket

class MacClient:
    """Minimal TCP server that waits for Mac GUI to connect
    then sends JSON lines. Usage:
        mac = MacClient(port=9000)
        mac.wait_for_conntion()
        mac.send_data(<json>)

    Notes:
    - NonBlocking connection after accept()
    - safe to call send_data() even if disconnected"""

    def __init__(self, host: str = "", port: int = 9000):
        self.host = host
        self.port = port
        self.listen_socket = None
        self.mac_connection = None
        self.elegoo = None

    def wait_for_connection(self):
        """Bind/listen once and wait for single inbound connection from Mac"""
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind((self.host, self.port))
        self.listen_socket.listen(1)
        print(f"[MAC] Waiting for connection port {self.port}....")
        self.mac_connection, addr = self.listen_socket.accept()
        self.mac_connection.setblocking(False)
        print(f"[MAC] Connected by {addr}")

    # --------- Data sending
    def send_helper(self, arduino_source: str, json_data: dict):
        """Adds 'Source' and 'time' to the received jsons before sending to Mac"""
        if not self.mac_connection:
            return
        try:
            outbound_json = OrderedDict()
            outbound_json["source"] = arduino_source
            outbound_json["time"] = time.time()
            outbound_json.update(json_data)
            self.mac_connection.sendall((json.dumps(outbound_json)+ '\n').encode('utf-8'))
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            print("[MAC] Disconnected")
            try:
                self.mac_connection.close()
            except Exception:
                pass
            self.mac_connection = None

    def send_nano_to_mac(self, nano_packet: NanoPacket):
        """Build nano json and send to mac"""
        json_data = {
            "mssg_id": nano_packet.NANO_MSSG_ID,
            "HEAD": nano_packet.HEAD,
            "F_USS": nano_packet.F_USS,
            "L_USS": nano_packet.L_USS,
            "R_USS": nano_packet.R_USS,
            "L_ENCD": nano_packet.L_ENCD,
            "R_ENCD": nano_packet.R_ENCD
        }
        self.send_helper("NANO", json_data)

    def send_elegoo_to_mac(self, elegoo_packet: ElegooPacket):
        """Send elegoo data to Mac"""
        if isinstance(elegoo_packet, ElegooPacket):
            json_data = {
                "mssg_id": elegoo_packet.ELEGOO_MSSG_ID,
                "L_motor": elegoo_packet.L_MTR_DATA,
                "R_motor": elegoo_packet.R_MTR_DATA
            }
        else:
            json_data = elegoo_packet
        self.send_helper("ELEGOO", json_data)

    def attach_elegoo(self, elegoo_port):
        self.elegoo = elegoo_port

    def send_to_elegoo_from_mac(self, mac_cmd):
        """
        Pass GUI command straight to Elegoo.
        Accepts JSON string or dict; SerialPort.write_json handles both.
        Returns True on success, False otherwise.
        """
        if self.elegoo is None:   # <— fix the attribute check
            return False
        return self.elegoo.write_json(mac_cmd)
        
    # ---- Receiver helper
    def recv_cmd(self):
        """NonBlocking read of one cmd line from Mac.
        Returns a decoded string or None if no Data """
        if not self.mac_connection:
            return None
        try:
            mac_cmd = self.mac_connection.recv(1024)
            if not mac_cmd:
                print("[MAC] Disconnected")
                self.mac_connection = None
                return None
            return mac_cmd.decode("utf-8", errors="ignore").strip()
        except (BlockingIOError, InterruptedError):
            return None
    