/*
  6/17/2025 Arduino Pi Mac Test script
  Purpose is to output the json message from the Arduino to the Pi to test from the Mac
  so that I don't need the motors or sensors hooked up to the Arduino.
*/
#include "OutputPrinter.h"
#include "SerialCommandHandler.h"

OutputPrinter printer(50);  // Print every x-ms
SerialCommandHandler serialHandler; // gGrabs serial 

motorstate_t currentState = STOP;
servostate_t servocurrentState = S_STOP;
unsigned long current_time;
unsigned long last_serial_time = 0;
unsigned long last_distance_update = 0;
unsigned long serial_timeout = 2500; // Time in ms for motor movement before having to enter annother cmd
float distance_in = 10;


void setup() {
  Serial.begin(115200);
}

void loop() {
  current_time = millis();

  motorstate_t newCommand;
  servostate_t newServoCommand;
  
  if (serialHandler.getCommand(newCommand, newServoCommand)) {
    currentState = newCommand;
    servocurrentState = newServoCommand;
    distance_in = 10;
    last_serial_time = current_time;
  }

  if (current_time - last_distance_update > 500) {
    last_distance_update = current_time;
    if (distance_in > 100) {
      distance_in = 10;
    } 
    distance_in++;
  }

  printer.json_print(distance_in, currentState, servocurrentState, current_time);  

}
