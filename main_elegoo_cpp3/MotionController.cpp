#include "MotionController.h"

MotionController::MotionController(MotorController &m)
  : motor(m), objectTooClose(false) {} // added the private servo thing

void MotionController::update(motorstate_t state_motor, float distance_in) {
  if (distance_in <= 2) {
    motor.stop();

    objectTooClose = true;
  } 
  else if (distance_in > 6 && objectTooClose) {
    objectTooClose = false;
    switch (state_motor) {
      case FORWARD:  motor.forward(); break;
      case BACKWARD: motor.backward(); break;
      case LEFT:     motor.turnLeft(); break;
      case RIGHT:    motor.turnRight(); break;
      case STOP:     motor.stop(); break;
    }
  }
  else if (!objectTooClose) {
    switch (state_motor) {
      case FORWARD:  motor.forward(); break;
      case BACKWARD: motor.backward(); break;
      case LEFT:     motor.turnLeft(); break;
      case RIGHT:    motor.turnRight(); break;
      case STOP:     motor.stop(); break;
    }
  }
}
