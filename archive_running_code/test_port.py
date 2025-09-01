#!/usr/bin/env python3
# pylint: disable=C0114,C0115,C0116,C0301,C0303,C0304
import json

# ---------------------------------------------------------------------------
# Optional: a no-hardware stub you can swap in for local testing on your Mac.
# It behaves like SerialPort but just prints what would be sent and lets you
# feed "incoming lines" by calling ._inject_line(...).
# ---------------------------------------------------------------------------
class DryRunPort:
    """
    Drop-in replacement for SerialPort when you have no hardware connected.
    Useful for unit tests and GUI-only runs.

    Example:
        nano = DryRunPort(parser=parse_nano_json)
        nano._inject_line('{"mssg_id":1,"F_USS":12,"L_USS":34,"R_USS":56,"HEAD":0}')
        pkt = nano.read_json()  # returns parsed NanoPacket
    """

    def __init__(self, json_parser=None, name="DRYRUN"):
        self.json_parser = json_parser
        self._queue = []
        self.name = name

    def has_data(self) -> bool:
        return bool(self._queue)

    def read_line(self):
        if not self._queue:
            return None
        return self._queue.pop(0)

    def read_json(self):
        line = self.read_line()
        if not line:
            return None
        if self.json_parser:
            return self.json_parser(line)
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return None

    def write_json(self, payload) -> bool:
        if hasattr(payload, "send_to_elegoo"):
            payload = payload.send_to_elegoo()
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        if not isinstance(payload, str):
            return False
        print(f"[{self.name} SEND]", payload)
        return True

    # Test helper: simulate that a line was received from the device.
    def _inject_line(self, line: str) -> None:
        self._queue.append(line)