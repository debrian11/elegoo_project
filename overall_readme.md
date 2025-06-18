# Project Overview

This project is a multi-component robotics system composed of:

* **Mac GUI**: Sends commands and receives telemetry.
* **Raspberry Pi**: Acts as a relay node, forwarding commands to Arduino and telemetry back to the Mac.
* **Arduino 1**: Controls motors and ultrasonic sensors.
* **Arduino 2**: (Planned) Will handle encoders and possibly MPU6050 sensor input.

# 🧠 System Architecture

```
[Mac GUI] <--> TCP <--> [Pi] <--> Serial <--> [Arduino 1] (motors + ultrasonic)
```

---

#  Arduino Code Summary (Arduino 1)

## **Core Purpose**

Reads ultrasonic sensor input and receives motor/servo commands from Pi over serial. Controls:

* 2 motors
* 1 servo (sweeping or stopped)
* Distance-based collision logic

### 🔧 Files and Roles:

#### `main_elegoo_cpp4.ino`

* Arduino main loop.
* Manages timing for:

  * Distance reading
  * Serial command checking
  * JSON output

#### `MotorController.*`

* Controls dual motor H-bridge pins:

  * Forward, backward, left, right, stop.
  * Adjustable PWM speed.

#### `MotionController.*`

* Adds logic for obstacle avoidance:

  * If object detected within 6", initiates a turn.
  * After a brief turn, resumes last movement.

#### `Servo_custom.*`

* Implements servo sweep or stop.
* Non-blocking sweep or simple sweep2 routine.

#### `ServoMotionController.*`

* Coordinates servo behavior using distance input and desired state.

#### `SerialCommandHandler.*`

* Parses single-byte serial commands (`f`, `b`, `s`, `z`, etc.).
* Maps them to enums for motor and servo states.

#### `UltraSonicSensor.*`

* Wraps `NewPing` library.
* Returns distance in inches (\~every 50 ms).

#### `OutputPrinter.*`

* Periodically prints telemetry:

  * As plain-text or JSON
  * Includes servo state, motor state, and distance

---

#  Raspberry Pi Code Summary

## **Core Purpose**

Acts as the central bridge:

* **Serial read/write** with Arduino
* **TCP socket server** for Mac
* **Streams USB camera video via UDP** to the Mac

### 🔧 Files:

#### `pi_serial_json.py`

* Detects Arduino automatically via `serial.tools.list_ports`
* Opens TCP socket on port `9000`
* Starts video streaming via `ffmpeg` (calls `pi_stream_video_usb`)
* Loop:

  * Read Arduino JSON telemetry
  * Forward to Mac
  * Receive Mac commands
  * Forward to Arduino

#### `pi_stream_video_usb.py`

* Launches a UDP `ffmpeg` stream from `/dev/video0` to Mac IP `192.168.0.21:1235`

---

#  Mac GUI Code Summary

## **Core Purpose**

A desktop interface to:

* Send serial-like commands to the Pi
* View telemetry (motor, servo, distance)
* Launch/stop video stream

### 🔧 Files:

#### `mac_gui_1.0.0.0.py`

* Assembles the GUI using `tkinter`
* Calls helpers from `gui_modules.py`
* Provides buttons to:

  * Send `f`, `b`, `l`, `r`, `s`, `z` over TCP
  * Launch or stop ffplay UDP video

#### `gui_modules.py`

* Modular setup of:

  * TCP socket connection to Pi
  * GUI layout + status labels
  * Button callbacks
  * Receives and parses JSON telemetry
  * Displays servo/motor/distance in GUI

---

# 🕓 Project Timeline Summary

###  April 2025

* Initial Arduino 1 work (motors, servo, ultrasonic sensor)
* Wrote modular C++ Arduino code (non-blocking, distance aware)

###  May 2025

* Shifted focus to Raspberry Pi
* Built TCP relay + serial bridge in Python
* Confirmed Pi ↔ Arduino serial comms

###  June 2025

* Developed Mac GUI in Python with `tkinter`
* Video streaming (ffmpeg to ffplay over UDP) confirmed working
* Full loop functional: Mac GUI ↔ Pi ↔ Arduino 1

### 🔜 Near Future Plans

* Integrate Arduino 2 for encoders and MPU6050
* Add feedback to adjust motor PWM dynamically (PID-style)
* Map-building/logging from telemetry stream

---

# Suggestions

* Add `README.md` per module directory
* Maintain `NOTES.md` to help future-you document quirks and design intent
* Consider simple flowchart diagram for README or interviews
