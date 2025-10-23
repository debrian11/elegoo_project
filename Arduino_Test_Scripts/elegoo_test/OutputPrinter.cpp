#include "OutputPrinter.h"
#include <Arduino.h>
#include <ArduinoJson.h>  // Install ArduinoJson from Library Manager


void OutputPrinter::json_print(int motor_pwm, unsigned long current_time) {
  if (current_time - lastPrintTime >= interval) {
    lastPrintTime = current_time;

    StaticJsonDocument<300> arduino_json_doc; // make a labeled data called "doc" the size of 200 bytes
    
    // Add values to the json doc; same syntax in c++
    arduino_json_doc["mssg_id"] = mssg_id++;
    arduino_json_doc["L_motor"] = motor_pwm;
    arduino_json_doc["R_motor"] = motor_pwm;

    serializeJson(arduino_json_doc, Serial); // having 2nd variable as Serial sends json directly to serial port
    Serial.println();  // To end with newline for easier parsing
  }
}
