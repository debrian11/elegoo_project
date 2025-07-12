#include "OutputPrinter.h"
#include <Arduino.h>

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

void OutputPrinter::print(int distance_in, motorstate_t currentState, unsigned long current_time) {
  if (current_time - lastPrintTime >= interval) {
    lastPrintTime = current_time;
    Serial.print("in: "); Serial.print(distance_in);
    Serial.print(" | MotorState: "); Serial.println(motorStateToString(currentState));
  }
}
