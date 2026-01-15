// 09/02/2025
// This script outputs the json key value pairs the nano normally sends

#include "OutputPrinter.h"
OutputPrinter serial_printer(50);  // Print every x-ms
unsigned long current_time;
unsigned long last_motor_update = 0;
int motor_pwm = 10;

void setup() {
  Serial.begin(115200);
}


void loop() {
  current_time = millis();

// For test purposes only in simulating a changing distance output of Ultrasonic
  if (current_time - last_motor_update > 100) {
    last_motor_update = current_time;
    if (motor_pwm > 100) {
      motor_pwm = 10;
    } 
    motor_pwm++;
  }

  // Output the motor speed and Ultrasonic distance back
  serial_printer.json_print(motor_pwm, current_time);
}
