#ifndef MOTION_CONTROLLER_H
#define MOTION_CONTROLLER_H

#include "MotorController.h"
#include "OutputPrinter.h"

class MotionController {
private:
  MotorController &motor;
  bool objectTooClose;

public:
  MotionController(MotorController &m);
  void update(motorstate_t state, float distance_in);
};

#endif
