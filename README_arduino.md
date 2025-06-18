
# Project Overview

This project is a multi-component robotics system composed of:

* **Macbook Air*: Sends commands and receives telemetry.
* **Raspberry Pi**: Acts as a relay node, forwarding commands to Arduino and telemetry back to the Mac.
* **Arduino 1**: Controls motors and ultrasonic sensors.
* **Arduino 2**: (Planned) Will handle encoders and possibly MPU6050 sensor input.

# 🧠 System Architecture

```
[Mac GUI] <--> TCP <--> [Pi] <--> Serial <--> [Arduino 1] (motors + ultrasonic)
```

# Arduino Code Summary (Arduino 1)

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
