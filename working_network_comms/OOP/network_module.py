#!/usr/bin/env python3
# pylint: disable=C0114,C0115,C0116,C0301,C0303,C0304,W0105
# 8/31/2025 add dataclass

#import os
from __future__ import annotations
import json
import time
import socket
from dataclasses import dataclass, field
from parsing_modules import ElegooPacket, NanoPacket

@dataclass
class MacClient:
    host: str = ""
    port: int = 9000
    listen_socket: socket.socket | None = None
    mac_connection: socket.socket | None = None
    elegoo: object | None = None
    rxbuf: str = field(default_factory=str)

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
    def send_nano_to_mac(self, nano_packet: NanoPacket):
        """Build nano json and send to mac"""
        if not self.mac_connection:
            return
        try:
            json_data = {
                "mssg_id": nano_packet.NANO_MSSG_ID,
                "HEAD": nano_packet.HEAD,
                "F_USS": nano_packet.F_USS,
                "L_USS": nano_packet.L_USS,
                "R_USS": nano_packet.R_USS,
                "L_ENCD": nano_packet.L_ENCD,
                "R_ENCD": nano_packet.R_ENCD
            }
            final_json = { "source": "NANO", "time": time.time(), **json_data}
            self.mac_connection.sendall((json.dumps(final_json)+ '\n').encode('utf-8'))

        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            print("[MAC] Disconnected")
            try:
                self.mac_connection.close()
            except Exception:
                pass
            self.mac_connection = None

    def send_elegoo_to_mac(self, elegoo_packet: ElegooPacket):
        """Send elegoo data to Mac"""
        if not self.mac_connection:
            return
        try:
            json_data = {
                "mssg_id": elegoo_packet.ELEGOO_MSSG_ID,
                "L_motor": elegoo_packet.L_MTR_DATA,
                "R_motor": elegoo_packet.R_MTR_DATA
            }
            final_json = { "source": "ELEGOO", "time": time.time(), **json_data}
            self.mac_connection.sendall((json.dumps(final_json)+ '\n').encode('utf-8'))
            
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            print("[MAC] Disconnected")
            try:
                self.mac_connection.close()
            except Exception:
                pass
            self.mac_connection = None

    def attach_elegoo(self, elegoo_port):
        self.elegoo = elegoo_port

    def send_to_elegoo_from_mac(self, mac_cmd):
        """
        Pass GUI command straight to Elegoo.
        Accepts JSON string or dict; SerialPort.write_json handles both.
        Returns True on success, False otherwise.
        """
        if self.elegoo is None:
            return False
        return self.elegoo.write_json(mac_cmd)
        
    # ---- Receiver helper
    def recv_cmd(self):
        """NonBlocking read; return the most recent complete JSON line."""
        if not self.mac_connection:
            return None
        try:
            chunk = self.mac_connection.recv(1024)
            if not chunk:
                print("[MAC] Disconnected")
                self.mac_connection = None
                return None
            self.rxbuf += chunk.decode("utf-8", errors="ignore")

            last_line = None
            while "\n" in self.rxbuf:
                line, _, rest = self.rxbuf.partition("\n")
                self.rxbuf = rest  # <- also fixes the original _rxbuf typo
                s = line.strip()
                if s:
                    last_line = s
            return last_line
        except (BlockingIOError, InterruptedError):
            return None
