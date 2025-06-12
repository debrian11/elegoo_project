#include "MotionController.h"

MotionController::MotionController(MotorController &m)
  : motor(m), objectTooClose(false) {} 

/* for the car to just STOP when object is detected
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
*/

void MotionController::update(motorstate_t state_motor, float distance_in) {
  unsigned long currentmotor_time = millis();

  // If too close, start turning left (non-blocking)
  if (distance_in <= 2 && !isTurningLeft) {
    objectTooClose = true;
    isTurningLeft = true;
    turnStartTime = currentmotor_time;
    motor.turnLeft();
    return;
  }

  // If currently turning, check if duration elapsed
  if (isTurningLeft) {
    if (currentmotor_time  - turnStartTime >= turnDuration) {
      isTurningLeft = false;
      objectTooClose = false;

      // Resume normal motion
      switch (state_motor) {
        case FORWARD:  motor.forward(); break;
        case BACKWARD: motor.backward(); break;
        case LEFT:     motor.turnLeft(); break;
        case RIGHT:    motor.turnRight(); break;
        case STOP:     motor.stop(); break;
      }
    }
    return; // Exit early while turning
  }

  // Normal control when no obstacle
  if (!objectTooClose) {
    switch (state_motor) {
      case FORWARD:  motor.forward(); break;
      case BACKWARD: motor.backward(); break;
      case LEFT:     motor.turnLeft(); break;
      case RIGHT:    motor.turnRight(); break;
      case STOP:     motor.stop(); break;
    }
  }
}
