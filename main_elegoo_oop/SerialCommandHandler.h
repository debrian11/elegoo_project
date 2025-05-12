#ifndef SERIAL_COMMAND_HANDLER_H
#define SERIAL_COMMAND_HANDLER_H

#include <Arduino.h>
#include "OutputPrinter.h"  // for motorstate_t enum

class SerialCommandHandler {
public:
  SerialCommandHandler() {}

  // Returns true if a command was read and updates the reference param
  bool getCommand(motorstate_t &commandOut) {
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
    return false; // nothing to read
  }
};

#endif
