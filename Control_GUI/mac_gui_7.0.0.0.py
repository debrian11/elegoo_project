#!/usr/bin/env python3
#pylint: disable=C0103,C0114,C0115,C0116,C0301,C0303,C0304

import tkinter as tk
import socket
import select
import json
import subprocess
from dataclasses import dataclass
from typing import Optional, Tuple
import math

# Pi variables
pi_1 = "192.168.0.63"
pi_2 = "192.168.0.226"

# ------------------------ Configuration ------------------------ #
# House defaults. Each cell is 1 ft.
GRID_WIDTH_FT  = 50   
GRID_LENGTH_FT = 50   
CELL_FT = 1.0         # occupancy cell size (1x1 ft)
PX_PER_FT = 8         # map scale (pixels per foot) -> 80 ft = 640 px width

# Encoder calibration (ticks per foot)
TICKS_PER_FOOT = 111

# Video command
VIDEO_CMD = [
    "ffplay",
    "-fflags", "nobuffer",
    "-flags", "low_delay",
    "-framedrop",
    "-vf", "setpts=0",
    "udp://@:12345"
]

# ------------------------ Utility ------------------------ #
def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def user_heading_to_math_deg(heading_deg: float) -> float:
    return (360.0 + (270.0 - float(heading_deg))) % 360.0

# ------------------------ Occupancy Grid ------------------------ #
class OccupancyGrid:
    """2D occupancy grid with 1 ft cells: 0=unknown, 1=free, 2=occupied."""
    def __init__(self, width_ft: int, height_ft: int):
        self.w = int(width_ft)
        self.h = int(height_ft)
        self.grid = [[0 for _ in range(self.w)] for _ in range(self.h)]

    def clear(self):
        for y in range(self.h):
            row = self.grid[y]
            for x in range(self.w):
                row[x] = 0

    def mark_cell(self, x_ft: float, y_ft: float, value: int):
        x = int(x_ft)
        y = int(y_ft)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.grid[y][x] = max(self.grid[y][x], value)

    def raycast_mark(self, x0_ft: float, y0_ft: float, theta_rad: float, distance_ft: float):
        steps = max(1, int(distance_ft / CELL_FT))
        for i in range(1, steps + 1):
            xf = x0_ft + (i * CELL_FT) * math.cos(theta_rad)
            yf = y0_ft + (i * CELL_FT) * math.sin(theta_rad)
            if i < steps:
                self.mark_cell(xf, yf, 1)  # free
            else:
                self.mark_cell(xf, yf, 2)  # occupied

# ------------------------ Occupancy Map Window ------------------------ #
class MapWindow:
    def __init__(self, root: tk.Tk, width_ft: int, height_ft: int):
        self.top = tk.Toplevel(root)
        self.top.title("Occupancy Map (NANO)")
        self.width_ft = width_ft
        self.height_ft = height_ft
        self.canvas_w = int(width_ft * PX_PER_FT)
        self.canvas_h = int(height_ft * PX_PER_FT)
        # place to the right of main
        self.top.geometry(f"{self.canvas_w}x{self.canvas_h}+50+50")
        self.canvas = tk.Canvas(self.top, width=self.canvas_w, height=self.canvas_h, bg="#111111", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self._draw_grid_lines()

    def _draw_grid_lines(self):
        g = self.canvas
        # light grid every cell
        for x in range(0, self.canvas_w+1, int(PX_PER_FT)):
            g.create_line(x, 0, x, self.canvas_h, fill="#222222")
        for y in range(0, self.canvas_h+1, int(PX_PER_FT)):
            g.create_line(0, y, self.canvas_w, y, fill="#222222")

    def _to_screen(self, x_ft: float, y_ft: float) -> Tuple[int, int]:
        # grid origin (0,0) at bottom-left; canvas origin at top-left -> invert y
        sx = int(x_ft * PX_PER_FT)
        sy = int(self.canvas_h - y_ft * PX_PER_FT)
        return sx, sy

    def redraw(self, grid: OccupancyGrid, robot_pose: Tuple[float, float, float]):
        # full redraw
        self.canvas.delete("cell")
        # draw occupied and free cells
        for gy in range(grid.h):
            row = grid.grid[gy]
            for gx in range(grid.w):
                val = row[gx]
                if val == 0:
                    continue
                # cell rectangle
                x0 = int(gx * PX_PER_FT)
                y0 = int(self.canvas_h - (gy+1) * PX_PER_FT)
                x1 = int((gx+1) * PX_PER_FT)
                y1 = int(self.canvas_h - (gy) * PX_PER_FT)
                if val == 1:   # free
                    color = "#1e3a5f"
                else:          # occupied
                    color = "#8b1e1e"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="", tags="cell")

        # draw robot figure
        x_ft, y_ft, theta_rad = robot_pose
        sx, sy = self._to_screen(x_ft, y_ft)
        r = 4  # pixel radius
        self.canvas.create_oval(sx-r, sy-r, sx+r, sy+r, fill="#dddddd", outline="", tags="cell")
        # heading line
        hx = sx + int(10 * math.cos(theta_rad))
        hy = sy - int(10 * math.sin(theta_rad))  # minus because screen y increases down
        self.canvas.create_line(sx, sy, hx, hy, fill="#dddddd", width=2, tags="cell")

# ------------------------ Motor State & GUI ------------------------ #
@dataclass
class MotorState:
    left_mult: float = 0.0
    right_mult: float = 0.0
    left_dir: int = 1
    right_dir: int = 1

class MacCarGUI:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

        # --- state ---
        self.sock: Optional[socket.socket] = None
        self.ffplay: Optional[subprocess.Popen] = None
        self.last_pi_line: str = ""
        self.motors = MotorState()
        self._reconnect_ms = 1000  # retry every 1s if disconnected

        # pose (feet, radians). Start at 0,0 will be set by NANO
        self.x_ft = 0.0
        self.y_ft = 0.0
        self.theta_rad = 0.0  # math radians
        self.prev_L = None  # previous left encoder
        self.prev_R = None  # previous right encoder

        # occupancy
        self.ogrid = OccupancyGrid(GRID_WIDTH_FT, GRID_LENGTH_FT)
        self.map_win: Optional[MapWindow] = None

        # --- Tk setup ---
        self.root = tk.Tk()
        self.root.title("Control GUI")

        self.conn_status = tk.StringVar(value="Status: Disconnected")
        self.mac_sent_status = tk.StringVar(value="Mac Send Status:")

        # Elegoo telemetry
        self.elegoo_mssg_id = tk.StringVar(value="Message ID: ---")
        self.left_motor_pwm  = tk.StringVar(value="Left Motor PWM: ---")
        self.right_motor_pwm = tk.StringVar(value="Right Motor PWM: ---")

        # Nano telemetry
        self.nano_mssg_id    = tk.StringVar(value="Message ID: ---")
        self.heading_status  = tk.StringVar(value="Heading: ---")
        self.left_enc        = tk.StringVar(value="Left Encoder: ---")
        self.right_enc       = tk.StringVar(value="Right Encoder: ---")
        self.f_uss           = tk.StringVar(value="Front USS: ---")
        self.l_uss           = tk.StringVar(value="Left USS: ---")
        self.r_uss           = tk.StringVar(value="Right USS: ---")

        # User PWM (default 0) and mirrors
        self.user_pwm        = tk.IntVar(value=0)  # IntVar instead of StringVar
        self.entered_pwm     = tk.StringVar(value="Entered: — %")
        self.computed_pwm    = tk.StringVar(value="Computed base PWM: —")

        self._build_ui()
        self._connect()
        self._update_pwm_labels()
        self._tick()
        # Autostart video and map window
        self.launch_video()
        self.open_map()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------- UI ----------------
    def _build_ui(self):
        # Window size/position
        gui_w, gui_h = 900, 540
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        cx, cy = int(sw/2 - gui_w/2), int(sh/2 - gui_h/2)
        self.root.geometry(f"{gui_w}x{gui_h}+{cx}+{cy}")

        # Title and status
        title = tk.Frame(self.root)
        title.pack(fill="x", pady=8)
        tk.Label(title, text="Elegoo Motor Telemetry", font=("Helvetica", 20, "bold")).pack(side="left", padx=10)
        tk.Label(title, textvariable=self.conn_status).pack(side="right", padx=10)

        # Two-column telemetry area
        row = tk.Frame(self.root)
        row.pack(padx=10, pady=10, fill="x")
        left = tk.Frame(row)
        left.pack(side="left", padx=20, anchor="n")
        right = tk.Frame(row)
        right.pack(side="left", padx=60, anchor="n")

        # Left column: Elegoo
        tk.Label(left, textvariable=self.elegoo_mssg_id).pack(anchor="w")
        tk.Label(left, textvariable=self.left_motor_pwm).pack(anchor="w")
        tk.Label(left, textvariable=self.right_motor_pwm).pack(anchor="w")
        tk.Label(left, textvariable=self.mac_sent_status, wraplength=500, justify="left").pack(anchor="w", pady=(10,0))

        # Controls under Elegoo
        controls = tk.Frame(left)
        controls.pack(anchor="w", pady=(12, 0))
        scale = tk.Scale(
            controls,
            from_=0, to=100,
            orient="horizontal",
            variable=self.user_pwm,
            length=200,
            label="PWM 0-> 100%"
        )
        scale.grid(row=0, column=0, columnspan=1, pady=4)
        tk.Label(controls, textvariable=self.entered_pwm).grid(row=1, column=0, padx=8, sticky="w")
        tk.Label(controls, textvariable=self.computed_pwm).grid(row=1, column=1, sticky="w")

        btns = tk.Frame(left)
        btns.pack(anchor="w", pady=10)
        tk.Button(btns, text="Forward", command=self.cmd_forward, width=10).grid(row=0, column=0, padx=4, pady=2)
        tk.Button(btns, text="Back",    command=self.cmd_back,    width=10).grid(row=0, column=1, padx=4, pady=2)
        tk.Button(btns, text="Left",    command=self.cmd_left,    width=10).grid(row=1, column=0, padx=4, pady=2)
        tk.Button(btns, text="Right",   command=self.cmd_right,   width=10).grid(row=1, column=1, padx=4, pady=2)
        tk.Button(btns, text="Stop",    command=self.cmd_stop,    width=10).grid(row=2, column=0, columnspan=2, pady=6)

        # Video and window controls
        video = tk.Frame(left)
        video.pack(anchor="w", pady=6)
        tk.Button(video, text="Launch Video Stream", command=self.launch_video, width=20).grid(row=0, column=0, padx=4, pady=2)
        tk.Button(video, text="Stop Video Stream",   command=self.stop_video,   width=20).grid(row=0, column=1, padx=4, pady=2)
        tk.Button(video, text="Open Map Window",     command=self.open_map,     width=20).grid(row=1, column=0, padx=4, pady=2)
        tk.Button(video, text="Close GUI",           command=self._on_close,    width=20).grid(row=1, column=1, padx=4, pady=2)

        # Right column: Nano
        tk.Label(right, text="NANO Encoder Telemetry", font=("Helvetica", 16, "bold")).pack(anchor="w", pady=(0,8))
        for v in (self.nano_mssg_id, self.heading_status, self.left_enc, self.right_enc,
                  self.f_uss, self.l_uss, self.r_uss):
            tk.Label(right, textvariable=v).pack(anchor="w")

        # Track PWM entry
        self.user_pwm.trace_add("write", self._update_pwm_labels)
        # --- Keyboard control (press = move, release = stop) ---
        self._pressed_keys = set()

        movement_keys = {
            "up": "forward", "w": "forward", "f": "forward",
            "down": "back",  "s": "back",    "b": "back",
            "left": "left",  "a": "left",    "l": "left",
            "right":"right", "d": "right",   "r": "right",
        }

        def on_key_press(e):
            k = (e.keysym or "").lower()
            action = movement_keys.get(k)

            if action:
                # ignore key auto-repeat
                if k not in self._pressed_keys:
                    self._pressed_keys.add(k)
                    if action == "forward": self.cmd_forward()
                    elif action == "back":  self.cmd_back()
                    elif action == "left":  self.cmd_left()
                    elif action == "right": self.cmd_right()
                if isinstance(e.widget, tk.Entry):
                    return "break"
                return "break"

            if k == "space":
                self.cmd_stop()
                return "break"
            if k == "escape":
                self._on_close()
                return "break"
            # let other keys propagate normally (no 'break' here)

        def on_key_release(e):
            k = (e.keysym or "").lower()
            self._pressed_keys.discard(k)

            # Stop only when *no* movement keys remain down
            if not any(name in self._pressed_keys for name in movement_keys):
                self.cmd_stop()

            # prevent default bubbling of these controls
            if k in movement_keys or k in ("space", "escape"):
                return "break"

        # Bind to the whole app so it works regardless of focus
        self.root.bind_all("<KeyPress>", on_key_press)
        self.root.bind_all("<KeyRelease>", on_key_release)


    # ------------- networking -------------
    def _connect(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            s.connect((self.ip, self.port))
            s.setblocking(False)
            self.sock = s
            self.conn_status.set("Status: Connected")
        except Exception as e:
            print(f"[MAC] connect failed: {e}")
            self.sock = None
            self.conn_status.set("Status: Disconnected")

    def _tick(self):
        if self.sock is None:
            # reconnect
            self.root.after(self._reconnect_ms, self._connect)
        else:
            self._read_once()
        self.root.after(100, self._tick)

    def _read_once(self):
        assert self.sock is not None
        try:
            rd, _, _ = select.select([self.sock], [], [], 0.1)
            if self.sock in rd:
                chunk = self.sock.recv(4096)
                if not chunk:
                    # orderly close
                    self.sock.close()
                    self.sock = None
                    self.conn_status.set("Status: Disconnected")
                    return
                for line in chunk.decode().splitlines():
                    if not line or line == self.last_pi_line:
                        continue
                    self._apply_json(line)
                    self.last_pi_line = line
        except Exception as e:
            print(f"[MAC] socket error: {e}")
            try:
                if self.sock:
                    self.sock.close()
            finally:
                self.sock = None
                self.conn_status.set("Status: Disconnected")

    # ------------- JSON handling -------------
    def _apply_json(self, line: str):
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            print(f"[MAC] bad JSON: {line}")
            return

        src = data.get("source")
        if src == "ELEGOO":
            self.elegoo_mssg_id.set(f"Message ID: {data.get('mssg_id','N/A')}")
            self.left_motor_pwm.set(f"Left Motor PWM: {data.get('L_motor','N/A')}")
            self.right_motor_pwm.set(f"Right Motor PWM: {data.get('R_motor','N/A')}")
        elif src == "NANO":
            self.nano_mssg_id.set(f"Message ID: {data.get('mssg_id','N/A')}")
            head = float(data.get('HEAD', 0.0))
            self.heading_status.set(f"Heading: {head}")
            self.left_enc.set(f"Left Encoder: {data.get('L_ENCD','N/A')}")
            self.right_enc.set(f"Right Encoder: {data.get('R_ENCD','N/A')}")
            self.f_uss.set(f"Front USS: {data.get('F_USS','N/A')}")
            self.l_uss.set(f"Left USS: {data.get('L_USS','N/A')}")
            self.r_uss.set(f"Right USS: {data.get('R_USS','N/A')}")
            self._update_pose_and_grid_from_nano(data)

    # ------------- Pose + Grid update -------------
    def _update_pose_and_grid_from_nano(self, data: dict):
        # heading
        try:
            user_deg = float(data.get("HEAD", 0.0))
        except Exception:
            user_deg = 0.0
        math_deg = user_heading_to_math_deg(user_deg)
        self.theta_rad = math.radians(math_deg)

        # encoders -> distance
        try:
            L = int(data.get("L_ENCD", 0))
            R = int(data.get("R_ENCD", 0))
        except Exception:
            L, R = 0, 0

        if self.prev_L is not None and self.prev_R is not None:
            dL = L - self.prev_L
            dR = R - self.prev_R
            dist_ft = ((dL + dR) / 2.0) / max(1e-6, TICKS_PER_FOOT)
            # dead-reckon translation using heading
            self.x_ft += dist_ft * math.cos(self.theta_rad)
            self.y_ft += dist_ft * math.sin(self.theta_rad)
            # clamp to map bounds
            self.x_ft = clamp(self.x_ft, 0.0, GRID_WIDTH_FT - 1e-3)
            self.y_ft = clamp(self.y_ft, 0.0, GRID_LENGTH_FT - 1e-3)
        self.prev_L, self.prev_R = L, R

        # ultrasonic updates (feet)
        def inches_to_ft(v):
            try:
                return float(v) / 12.0
            except Exception:
                return None

        F = inches_to_ft(data.get("F_USS", None))
        Ld = inches_to_ft(data.get("L_USS", None))
        Rd = inches_to_ft(data.get("R_USS", None))

        if F is not None:
            self.ogrid.raycast_mark(self.x_ft, self.y_ft, self.theta_rad, F)
        if Ld is not None:
            self.ogrid.raycast_mark(self.x_ft, self.y_ft, self.theta_rad + math.radians(90), Ld)
        if Rd is not None:
            self.ogrid.raycast_mark(self.x_ft, self.y_ft, self.theta_rad - math.radians(90), Rd)

        # redraw map if open
        if self.map_win:
            self.map_win.redraw(self.ogrid, (self.x_ft, self.y_ft, self.theta_rad))

    # ------------- PWM helpers -------------
    def _update_pwm_labels(self, *_):
        try:
            p = float(self.user_pwm.get())
            self.entered_pwm.set(f"Entered: {p:.0f} %")
        except ValueError:
            self.entered_pwm.set("Entered: — %")
        self.computed_pwm.set(f"Computed base PWM: {self._base_pwm()}")

    def _base_pwm(self) -> int:
        """Map 0–100% to 85–150 linearly."""
        try:
            pct = float(self.user_pwm.get())
        except ValueError:
            pct = 0.0
        pct = max(0.0, min(100.0, pct))
        return int(85 + 0.65 * pct)  # 85 + (150-85)/100 * pct

    def _build_motor_json(self) -> str:
        m = self.motors
        base = self._base_pwm()
        payload = {
            "L_DIR": m.left_dir,
            "R_DIR": m.right_dir,
            "L_PWM": int(base * m.left_mult),
            "R_PWM": int(base * m.right_mult),
        }
        return json.dumps(payload)

    def _safe_send(self, tag: str):
        msg = self._build_motor_json()
        if self.sock is None:
            self.mac_sent_status.set(f"Mac Send Status: {tag} | NOT SENT (disconnected)")
            return
        try:
            self.sock.sendall((msg + "\n").encode("utf-8"))
            self.mac_sent_status.set(f"Mac Send Status: {tag} | Raw = {msg}")
            print(f"Sending {msg}")
        except Exception as e:
            print(f"[MAC] send failed: {e}")
            try:
                if self.sock:
                    self.sock.close()
            finally:
                self.sock = None
                self.conn_status.set("Status: Disconnected")

    # ------------- Robot commands -------------
    def cmd_forward(self, event=None):
        self.motors.left_mult, self.motors.right_mult = 1.0, 0.65
        self.motors.left_dir,  self.motors.right_dir  = 1, 1
        self._safe_send("forward")

    def cmd_back(self, event=None):
        self.motors.left_mult, self.motors.right_mult = 0.75, 0.64
        self.motors.left_dir,  self.motors.right_dir  = 0, 0
        self._safe_send("back")

    def cmd_left(self, event=None):
        self.motors.left_mult, self.motors.right_mult = 0.5, 1.0
        self.motors.left_dir,  self.motors.right_dir  = 0, 1
        self._safe_send("left")

    def cmd_right(self, event=None):
        self.motors.left_mult, self.motors.right_mult = 0.8, 0.5
        self.motors.left_dir,  self.motors.right_dir  = 1, 0
        self._safe_send("right")

    def cmd_stop(self, event=None):
        self.motors.left_mult = self.motors.right_mult = 0.0
        self.motors.left_dir = self.motors.right_dir = 1
        self._safe_send("stop")

    # ------------- video + windows -------------
    def launch_video(self):
        if self.ffplay is not None:
            return
        try:
            self.ffplay = subprocess.Popen(VIDEO_CMD)
            self.mac_sent_status.set("Video: launched")
        except Exception as e:
            self.mac_sent_status.set(f"Video: failed to launch: {e}")

    def stop_video(self):
        try:
            if self.ffplay:
                self.ffplay.terminate()
                self.ffplay.wait(timeout=1)
                self.ffplay = None
                self.mac_sent_status.set("Video: stopped")
        except Exception as e:
            self.mac_sent_status.set(f"Video: stop error: {e}")

    def open_map(self):
        if self.map_win is None or not self.map_win.top.winfo_exists():
            self.map_win = MapWindow(self.root, GRID_WIDTH_FT, GRID_LENGTH_FT)
            # draw immediately
            self.map_win.redraw(self.ogrid, (self.x_ft, self.y_ft, self.theta_rad))
        else:
            self.map_win.top.lift()

    def _on_close(self):
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        try:
            if self.ffplay:
                self.ffplay.terminate()
                self.ffplay.wait(timeout=1)
        except Exception:
            pass
        if self.map_win and self.map_win.top.winfo_exists():
            try:
                self.map_win.top.destroy()
            except Exception:
                pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MacCarGUI(pi_1, 9000)
    #app = MacCarGUI(pi_2, 9000)
    app.run()
