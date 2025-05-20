#include "ServoSerialCommand.h"
// #include "SerialCommandHandler.h"
#include <Arduino.h>

bool ServoSerialCommand::getCommand(servostate_t &servocommandOut) {
  if (Serial.available()) { // returns true or false if serial availible
    char d = Serial.read();
    switch (d) {
      case 'z': servocommandOut = SWEEP; return true;
      case 'x': servocommandOut = S_STOP; return true;
      default:
        Serial.print("Unknown Servo command: ");
        Serial.println(d);
        return false;
    }
  }
  return false;
}
