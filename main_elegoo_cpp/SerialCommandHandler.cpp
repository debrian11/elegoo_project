#include "SerialCommandHandler.h"
#include <Arduino.h>

bool SerialCommandHandler::getCommand(motorstate_t &commandOut) {
  if (Serial.available()) {
    char c = Serial.read();
    switch (c) {
      case 'f': commandOut = FORWARD; return true;
      case 'b': commandOut = BACKWARD; return true;
      case 'l': commandOut = LEFT; return true;
      case 'r': commandOut = RIGHT; return true;
      case 's': commandOut = STOP; return true;
      default:
        Serial.print("Unknown command: ");
        Serial.println(c);
        return false;
    }
  }
  return false;
}
