void updateMotors(motorstate_t state, float distance_in) {
  switch (state) {
    case FORWARD:
      if (distance_in > 8) {
        motor.forward();
      } else if (distance_in < 3) {
        motor.stop();
      }
      break;

    case BACKWARD:
      if (distance_in > 8) {
        motor.backward();
      } else if (distance_in < 3) {
        motor.stop();
      }
      break;

    case LEFT:
      motor.turnLeft();
      break;

    case RIGHT:
      motor.turnRight();
      break;

    case STOP:
    default:
      motor.stop();
      break;
  }
}
