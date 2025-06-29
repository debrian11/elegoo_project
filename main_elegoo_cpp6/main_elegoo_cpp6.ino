/* 6/22/2025
This .ino will be the first interation in reading/cmding 2 inputs to each of the motors on left and right.
Encoders will eventually be integrated to a 2nd arduino so that those values adjust with the pwm cmds.

6/29/2025 
Add servo angle output to the JSON output
*/
#include "OutputPrinter.h"
#include "SerialCommandHandler.h"
#include "UltraSonicSensor.h"
#include "Servo_custom.h"
#include "Motorcontroller.h"

// Initial Motor Pins setup
int left_motor_pwm_pin = 6;
int right_motor_pwm_pin = 5;
int left_motor_direction_pin = 8;
int right_motor_direction_pin = 7;
int stby = 3;
MotorController motor(left_motor_direction_pin, right_motor_direction_pin,
                      left_motor_pwm_pin, right_motor_pwm_pin,
                      stby);

// Serial comms setup
SerialCommandHandler serialHandler(motor); // Grabs serial 

// Create objects:
UltrasonicSensor ultrasonic(13, 12); // (trig / echo)
OutputPrinter serial_printer(50);  // Print every x-ms

// Servo Setup:
int servo_pin = 11;
int servo_sweep_status = 0;
int current_angle;
Servo_custom servo1(servo_pin);

unsigned long current_time;
float distance_in = 10;

// Initial Motor Stuff
int left_motor_direction = 0;
int right_motor_direction = 0;
int left_motor_pwm = 0;
int right_motor_pwm = 0;

void setup() {
  Serial.begin(115200);
  servo1.servo_custom_begin();
  motor.begin();
}

void loop() {
  current_time = millis();

// Ultrasonic Sensor
  float new_distance = ultrasonic.getDistanceInches();
  if (new_distance > 0) {
    distance_in = new_distance;
  }

  // Parse the incoming Pi JSON for motor speed and direction
  serialHandler.getCommand_json(servo_sweep_status);
  servo1.servo_custom_sweep(servo_sweep_status);

  // Output the motor speed and Ultrasonic distance back
  //serial_printer.json_print(distance_in, left_motor_pwm, right_motor_pwm, cu,current_time);
  serial_printer.json_print(distance_in, motor, servo1, current_time);
}
