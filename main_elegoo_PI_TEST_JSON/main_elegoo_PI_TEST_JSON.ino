/*
  6/17/2025 Arduino Pi Mac Test script
  Purpose is to output the json message from the Arduino to the Pi to test from the Mac
  so that I don't need the motors or sensors hooked up to the Arduino.
*/
#include "OutputPrinter.h"
#include "SerialCommandHandler.h"

OutputPrinter serial_printer(50);  // Print every x-ms
SerialCommandHandler serialHandler; // gGrabs serial 

unsigned long current_time;
unsigned long last_serial_time = 0;
unsigned long last_distance_update = 0;
unsigned long serial_timeout = 2500; // Time in ms for motor movement before having to enter annother cmd
float distance_in = 10;

// Initial Motor Stuff
int L_MTR_DIR = 0;
int R_MTR_DIR = 0;
int L_MTR_PWM = 0;
int R_MTR_PWM = 0;

void setup() {
  Serial.begin(115200);
}

// ------------------------------------------------------------------------------------------//

void loop() {
  current_time = millis();

// For test purposes only in simulating a changing distance output of Ultrasonic
  if (current_time - last_distance_update > 500) {
    last_distance_update = current_time;
    if (distance_in > 100) {
      distance_in = 10;
    } 
    distance_in++;
  }

  // Parse the incoming Pi JSON for motor speed and direction
  serialHandler.getCommand_json(L_MTR_DIR, R_MTR_DIR, L_MTR_PWM, R_MTR_PWM);

  // Command the motors to move
  /* TBD here */

  // Output the motor speed and Ultrasonic distance back
  serial_printer.json_print(distance_in, L_MTR_PWM, R_MTR_PWM, current_time);
}
