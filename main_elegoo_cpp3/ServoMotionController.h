#ifndef SERVO_MOTION_CONTROLLER_H
#define SERVO_MOTION_CONTROLLER_H

#include "Servo_custom.h" // added
#include "OutputPrinter.h"

class ServoMotionController {
private:
  Servo_custom &private_servo; // added
  bool objectTooClose;


public:
  ServoMotionController(Servo_custom &ref_servo);
  void update(servostate_t state_servo, float distance_in);
};

#endif
