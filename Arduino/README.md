# Arduino
### 09/07/2025

The Arduino portion consist of 2 Arduinos:
1. **Arduino Elegoo Uno**
- Responsible for taking in motor pulse width module (PWM) and direction commands from the Raspberry Pi
- Will be denoted as *"Elegoo"* throughout this README

2. **Arduino Nano**
- Responsible for sending sensor data to the Raspberry Pi (ultrasonic sensor, heading, encoder)
- Will be denoted as *"Nano"* throughout this README

## Code installation 
All code is uploaded to each respective Arduino using the Arduino IDE 2.3.6 via USB.

## Arduino Elegoo
Code base for the Elegoo is in the **main_elegoo_cpp6** folder.
### Purpose ###
Control left and right motor PWM and directions of the robot car.
Sends json message format of PWM to Pi via serial.
Reads json message format from Mac GUI via the Pi to control motors.

#### `main_elegoo_cpp6.*`
* main arduino loop
* Manages timing for
    * Motor PWM and direction
    * Serial command checks
    * JSON output for telemetry

#### `Motorcontroller.*`
* Creates motor object for PWM and direction control

#### `OutputPrinter.*`
* Takes in motor PWM data and packages it up in a json before sending to the Pi via serial.

#### `SerialCommandHandler.*`
* Reads the incoming json message and sends to motor object for movement


## Arduino Nano
Code base for the Nano is in the **main_nano_cpp5** folder.
### Purpose ###
Read sensor data consisting of
 - 3 Ultrasonic sensors (left, forward, right)
 - 2 Optical encoders (rear right and left wheels)
 - 1 Magnometer (for heading)

#### `main_nano_cpp5.*`
* main arduino loop
* Initial setup of pulling calibrated magnometer from EEPROM for heading measurement
* Create 3 Ultrasonic sensor objects for each direction
* Manages timing for sensor reading and sending:
    * Ultrasonic, magmeter, encoders
    * JSON output for telemetry

#### `UltraSonicSensor.*`
* Creates an ultrasonic instance via the NewPing.h arduino library
* Converts the ultrasonic reading from cm to inches

#### `Encoder.*`
* Utilizes the 2 ISR pins on the nano to read optical sensors on the rear wheels.

#### `MagMeter.*`
* Reads magmeter heading values, only in the Z axis for 2-D heading values.

#### `OutputPrinter.*`
* Takes in all sensor data and packages it up in a json before sending to the Pi via serial.