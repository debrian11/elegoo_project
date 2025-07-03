/*
  6/17/2025 Arduino Pi Mac Test script
  Purpose is to output the json message from the Arduino to the Pi to test from the Mac
  so that I don't need the motors or sensors hooked up to the Arduino.
*/
#include "OutputPrinter.h"

OutputPrinter serial_printer(50);  // Print every x-ms

unsigned long current_time;
int left_encoder = 1;
int right_encoder = 1;
float last_time_update = 0;

void setup() {
  Serial.begin(115200);
}


void loop() {
  current_time = millis();

// For test purposes only in simulating a changing distance output of Ultrasonic
  if (current_time - last_time_update > 250) {
    last_time_update = current_time;
    left_encoder++;
    right_encoder++;
  }

  serial_printer.json_print(left_encoder, right_encoder, current_time);
}
