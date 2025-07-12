#ifndef SERIAL_COMMAND_HANDLER_H
#define SERIAL_COMMAND_HANDLER_H

#include <Arduino.h>
#include "OutputPrinter.h"  // for motorstate_t enum

class SerialCommandHandler {
public:
  SerialCommandHandler() {}
  bool getCommand(motorstate_t &commandOut, servostate_t &servocommandOut);
};

#endif
