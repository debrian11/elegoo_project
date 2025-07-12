#include "ServoMotionController.h"

ServoMotionController::ServoMotionController(Servo_custom &ref_servo)
  : private_servo(ref_servo) {}

void ServoMotionController::update(servostate_t state_servo, float distance_in) {
  if (distance_in <= 2) {
    private_servo.servo_custom_stop();

    objectTooClose = true;
  } 
  else if (distance_in > 6 && objectTooClose) {
    objectTooClose = false;
    switch (state_servo) {
      case SWEEP:  private_servo.servo_custom_sweep1(); break;
      case S_STOP: private_servo.servo_custom_stop(); break;
    }
  }
  else if (!objectTooClose) {
    switch (state_servo) {
      case SWEEP:  private_servo.servo_custom_sweep1(); break;
      case S_STOP: private_servo.servo_custom_stop(); break;
    }
  }
}
