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
