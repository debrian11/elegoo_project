#ifndef SERIAL_COMMAND_HANDLER_H
#define SERIAL_COMMAND_HANDLER_H

#include <Arduino.h>
#include "OutputPrinter.h"

class SerialCommandHandler {

public:
  SerialCommandHandler() {}

  //bool getCommand_json(int &L_MTR_DIR, int &R_MTR_DIR, int &L_MTR_PWM, int &R_MTR_PWM);
  bool getCommand_json(int &L_MTR_DIR, int &R_MTR_DIR, 
                       int &L_MTR_PWM, int &R_MTR_PWM,
                       int &L_MTR_DIR_PIN, int &R_MTR_DIR_PIN,
                       int &L_MTR_PWM_PIN, int &R_MTR_PWM_PIN,
                       int &SERVO_SWEEP_STATUS); 
};

#endif