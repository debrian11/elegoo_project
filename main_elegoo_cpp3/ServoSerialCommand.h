#ifndef SERVO_SERIAL_COMMAND_HANDLER_H
#define SERVO_SERIAL_COMMAND_HANDLER_H

#include <Arduino.h>
#include "OutputPrinter.h"  // for the servo_enum

class ServoSerialCommand {
public:
  ServoSerialCommand() {}
  bool getCommand(servostate_t &servocommandOut);
};

#endif
