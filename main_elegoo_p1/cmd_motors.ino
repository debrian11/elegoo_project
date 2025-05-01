void move_fwd() {
    digitalWrite(AIN1, HIGH);  // Right motors forward
    digitalWrite(BIN1, HIGH);  // Left motors forward
    analogWrite(PWMA, 100);    // Speed for right motor
    analogWrite(PWMB, 100);    // Speed for left motor
}

void move_back() {
    digitalWrite(AIN1, LOW);   // Right motors backward
    digitalWrite(BIN1, LOW);   // Left motors backward
    analogWrite(PWMA, 100);
    analogWrite(PWMB, 100);
}

void stop_motors() {
    analogWrite(PWMA, 0);
    analogWrite(PWMB, 0);
}

void updateMotors() {
  switch(currentmotorstate) {
    case FORWARD:
        move_fwd();
        break;
    case BACKWARD:
        move_back();
        break;
    case STOP:
    default:
        stop_motors();
        break;
    }
}