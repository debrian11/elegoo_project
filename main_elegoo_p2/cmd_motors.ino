void updateMotors() {
    switch(currentmotorstate) {
        case FORWARD:
            move_fwd();
            break;

        case BACKWARD:
            move_back();
            break;

        case STOP:
            stop_motors();
            break;

        case LEFT:
            left_turn();
            break;

        case RIGHT:
            right_turn();
            break;   
    }
}

void move_fwd() {
    if (distance_in > move_distance) {
    digitalWrite(AIN1, HIGH);  // Right motors forward
    digitalWrite(BIN1, HIGH);  // Left motors forward
    analogWrite(PWMA, 100);    // Speed for right motor
    analogWrite(PWMB, 100);    // Speed for left motor
    } else if (distance_in < stop_distance) {
        stop_motors();
    }
}

void move_back() {
    if (distance_in > move_distance) {
    digitalWrite(AIN1, LOW);   // Right motors backward
    digitalWrite(BIN1, LOW);   // Left motors backward
    analogWrite(PWMA, 100);
    analogWrite(PWMB, 100);
    } else if (distance_in < stop_distance) {
        stop_motors();
    }
}

void stop_motors() {
    analogWrite(PWMA, 0);
    analogWrite(PWMB, 0);
}

void left_turn() {
    if (current_time - motor_lastupdate >= 1000) {
        digitalWrite(AIN1, HIGH);   // Right motors backward
        digitalWrite(BIN1, LOW);   // Left motors backward
        analogWrite(PWMA, 100);
        analogWrite(PWMB, 100);
        stop_motors();
    }
}

void right_turn() {
    if (current_time - motor_lastupdate >= 1000) {
        digitalWrite(AIN1, LOW);   // Right motors backward
        digitalWrite(BIN1, HIGH);   // Left motors backward
        analogWrite(PWMA, 100);
        analogWrite(PWMB, 100);
        stop_motors();
    }
}