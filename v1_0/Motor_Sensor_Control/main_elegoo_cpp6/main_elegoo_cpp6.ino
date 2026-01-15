/* 6/22/2025
This .ino will be the first interation in reading/cmding 2 inputs to each of the motors on left and right.
Encoders will eventually be integrated to a 2nd arduino so that those values adjust with the pwm cmds.

6/29/2025 
Add servo angle output to the JSON output

7/10/2025 Removed Ultrasonic references and servo
*/
#include "OutputPrinter.h"
#include "SerialCommandHandler.h"
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

SerialCommandHandler serialHandler(motor); // Grabs serial 
OutputPrinter serial_printer(50);  // Print every x-ms
unsigned long current_time;

void setup() {
  Serial.begin(115200);
  motor.begin();
}

void loop() {
  current_time = millis();

  // Parse the incoming Pi JSON for motor speed and direction
  serialHandler.getCommand_json();

  // Output the motor speed and Ultrasonic distance back
  serial_printer.json_print(motor, current_time);
}
