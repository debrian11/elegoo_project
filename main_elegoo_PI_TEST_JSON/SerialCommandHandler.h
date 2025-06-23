#ifndef SERIAL_COMMAND_HANDLER_H
#define SERIAL_COMMAND_HANDLER_H

#include <Arduino.h>
#include "OutputPrinter.h"  // for motorstate_t enum

class SerialCommandHandler {
public:
  SerialCommandHandler() {}

  bool getCommand_json(int &L_MTR_DIR, int &R_MTR_DIR, int &L_MTR_PWM, int &R_MTR_PWM);
};

#endif
