#ifndef MOTION_CONTROLLER_H
#define MOTION_CONTROLLER_H

#include "MotorController.h"
#include "Servo_custom.h" // added
#include "OutputPrinter.h"

class MotionController {
private:
  MotorController &motor;
  Servo_custom &private_servo; // added

  bool objectTooClose;

public:
  MotionController(MotorController &m, Servo_custom &ref_servo);
  void update(motorstate_t state, float distance_in);
};

#endif
