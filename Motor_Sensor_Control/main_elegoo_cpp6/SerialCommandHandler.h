#ifndef SERIAL_COMMAND_HANDLER_H
#define SERIAL_COMMAND_HANDLER_H

#include <Arduino.h>
#include "OutputPrinter.h"
#include "Motorcontroller.h"

class SerialCommandHandler {

private:
  MotorController& _motor_object;


public:
  SerialCommandHandler(MotorController &motor_object) : _motor_object(motor_object){}

  //bool getCommand_json(int &L_MTR_DIR, int &R_MTR_DIR, int &L_MTR_PWM, int &R_MTR_PWM);
  bool getCommand_json(); 
};

#endif