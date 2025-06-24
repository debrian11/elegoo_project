/* 6/22/2025
This .ino will be the first interation in reading/cmding 2 inputs to each of the motors on left and right.
Encoders will eventually be integrated to a 2nd arduino so that those values adjust with the pwm cmds.
*/

#include "OutputPrinter.h"
#include "SerialCommandHandler.h"
#include "UltraSonicSensor.h"
#include "Servo_custom.h"
#include "Motorcontroller.h"

// Create objects:
UltrasonicSensor ultrasonic(13, 12); // (trig / echo)
int servo_pin = 11;
int servo_sweep_status = 0;
Servo_custom servo1(servo_pin);
OutputPrinter serial_printer(50);  // Print every x-ms
SerialCommandHandler serialHandler; // gGrabs serial 


unsigned long current_time;
unsigned long last_serial_time = 0;
unsigned long last_distance_update = 0;
float distance_in = 10;

// Initial Motor Stuff
int left_motor_direction = 0;
int right_motor_direction = 0;
int left_motor_pwm = 0;
int right_motor_pwm = 0;

// Initial Motor Pins setup
int left_motor_pwm_pin = 6;
int right_motor_pwm_pin = 5;
int left_motor_direction_pin = 8;
int right_motor_direction_pin = 7;
int stby = 3;
MotorController motor(left_motor_direction_pin, right_motor_direction_pin,
                      left_motor_pwm_pin, right_motor_pwm_pin,
                      stby);

void setup() {
  Serial.begin(115200);

  // Servo Setup
  servo1.servo_custom_begin();
  motor.begin();

  // Motor Setup 
  /*
  pinMode(left_motor_direction_pin, OUTPUT);
  pinMode(right_motor_direction_pin, OUTPUT);
  pinMode(left_motor_pwm_pin, OUTPUT);
  pinMode(right_motor_pwm_pin, OUTPUT);
  pinMode(stby, OUTPUT);
  digitalWrite(stby, HIGH);
  */
}

// ------------------------------------------------------------------------------------------//

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
  serial_printer.json_print(distance_in, left_motor_pwm, right_motor_pwm, current_time);
}
