#include "SerialCommandHandler.h"
#include <Arduino.h>



bool SerialCommandHandler::getCommand(motorstate_t &commandOut, servostate_t &servocommandOut) {
  if (Serial.available()) { // returns true or false if serial availible
    char c = Serial.read();
    switch (c) {
      case 'f': commandOut = FORWARD; return true;
      case 'b': commandOut = BACKWARD; return true;
      case 'l': commandOut = LEFT; return true;
      case 'r': commandOut = RIGHT; return true;
      case 's': commandOut = STOP; servocommandOut = S_STOP; return true;
      case 'z': servocommandOut = SWEEP; return true;
      //case 'x': servocommandOut = S_STOP; return true;
      default:
        Serial.print("Unknown command: ");
        Serial.println(c);
        return false;
    }
  }
  return false;
}
