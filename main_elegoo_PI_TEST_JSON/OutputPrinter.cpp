#include "OutputPrinter.h"
#include <Arduino.h>
#include <ArduinoJson.h>  // Install ArduinoJson from Library Manager

String OutputPrinter::motorStateToString(motorstate_t state) {
  switch (state) {
    case FORWARD: return "FORWARD";
    case BACKWARD: return "BACKWARD";
    case STOP: return "STOP";
    case LEFT: return "LEFT";
    case RIGHT: return "RIGHT";
    default: return "UNKNOWN";
  }
}

String OutputPrinter::servoStateToString(servostate_t s_state) {
  switch (s_state) {
    case SWEEP: return "SWEEP";
    case S_STOP: return "S_STOP";
    default: return "UNKNOWN SERVO";
  }
}

void OutputPrinter::print(int distance_in, motorstate_t currentState, servostate_t servocurrentState,  unsigned long current_time) {
  if (current_time - lastPrintTime >= interval) {
    lastPrintTime = current_time;
    Serial.print("Servo: "); Serial.print(servoStateToString(servocurrentState));
    Serial.print(" | Motor: "); Serial.print(motorStateToString(currentState));
    Serial.print(" | in: "); Serial.println(distance_in);
  }
}

void OutputPrinter::json_print(int distance_in, motorstate_t currentState, servostate_t servocurrentState, unsigned long current_time) {
  if (current_time - lastPrintTime >= interval) {
    lastPrintTime = current_time;

    StaticJsonDocument<200> doc; // make a labeled data called "doc" the size of 200 bytes
    
    // Add values to the json doc; same syntax in c++
    doc["servo"] = servoStateToString(servocurrentState);
    doc["motor"] = motorStateToString(currentState);
    doc["distance"] = distance_in;

    serializeJson(doc, Serial);
    Serial.println();  // To end with newline for easier parsing
  }
}