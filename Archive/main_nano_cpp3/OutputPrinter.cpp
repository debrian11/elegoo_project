#include "OutputPrinter.h"
#include <Arduino.h>
#include <ArduinoJson.h>  // Install ArduinoJson from Library Manager


void OutputPrinter::json_print(int front_sensor, int left_sensor, int right_sensor,
                               int left_encoder, int right_encoder, unsigned long current_time) {
  if (current_time - lastPrintTime >= interval) {
    lastPrintTime = current_time;
    StaticJsonDocument<300> arduino_json_doc; // make a labeled data called "doc" the size of 200 bytes
    
    // Add values to the json doc; same syntax in c++
    arduino_json_doc["mssg_id"] = mssg_id++;
    arduino_json_doc["F_USS"] = front_sensor;
    arduino_json_doc["L_USS"] = left_sensor;
    arduino_json_doc["R_USS"] = right_sensor;
    arduino_json_doc["L_ENCD"] = left_encoder;
    arduino_json_doc["R_ENCD"] = right_encoder;
    
    serializeJson(arduino_json_doc, Serial); // having 2nd variable as Serial sends json directly to serial port
    Serial.println();  // To end with newline for easier parsing
  }
}
