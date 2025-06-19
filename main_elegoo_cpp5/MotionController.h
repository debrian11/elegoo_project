#ifndef MOTION_CONTROLLER_H
#define MOTION_CONTROLLER_H

#include "MotorController.h"
#include "Servo_custom.h" // added
#include "OutputPrinter.h"

class MotionController {
private:
  MotorController &motor;
  bool objectTooClose;
  bool isTurningLeft = false;
  unsigned long turnStartTime = 0;
  const unsigned long turnDuration = 300; // time in milliseconds


public:
  MotionController(MotorController &m);
  void update(motorstate_t state_motor, float distance_in);
};

#endif
