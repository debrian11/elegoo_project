#include "OutputPrinter.h"
#include <Arduino.h>
#include <ArduinoJson.h>  // Install ArduinoJson from Library Manager


void OutputPrinter::json_print(int &left_encoder, int &right_encoder, unsigned long current_time) {
  if (current_time - lastPrintTime >= interval) {
    lastPrintTime = current_time;

    StaticJsonDocument<200> arduino_json_doc; // make a labeled data called "doc" the size of 200 bytes
    
    // Add values to the json doc; same syntax in c++
    // {"L_ENCD":0,"R_ENCD":0,"time":0}
    arduino_json_doc["L_ENCD"] = left_encoder;
    arduino_json_doc["R_ENCD"] = right_encoder;
    arduino_json_doc["time"] = current_time;
    // { "L_ENCD:left_encoder, "R_ENCD":right_encoder, "time":current_time}

    serializeJson(arduino_json_doc, Serial); // having 2nd variable as Serial sends json directly to serial port
    Serial.println();  // To end with newline for easier parsing
  }
}
