#include "OutputPrinter.h"
#include <Arduino.h>
#include <ArduinoJson.h>  // Install ArduinoJson from Library Manager


void OutputPrinter::json_print(int distance_in, int &left_motor_speed, int &right_motor_speed, unsigned long current_time) {
  if (current_time - lastPrintTime >= interval) {
    lastPrintTime = current_time;

    StaticJsonDocument<200> arduino_json_doc; // make a labeled data called "doc" the size of 200 bytes
    
    // Add values to the json doc; same syntax in c++
    arduino_json_doc["L_motor"] = left_motor_speed;
    arduino_json_doc["R_motor"] = right_motor_speed;
    arduino_json_doc["distance"] = distance_in;
    arduino_json_doc["time"] = current_time;
    // { "L_motor":left_motor_speed, "R_motor":right_motor_speed, "distance":0, "time":current_time}

    serializeJson(arduino_json_doc, Serial); // having 2nd variable as Serial sends json directly to serial port
    Serial.println();  // To end with newline for easier parsing
  }
}
