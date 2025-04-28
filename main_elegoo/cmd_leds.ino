void stby_state(int distance_in) {
    pot_state = "Stby";
    // digitalWrite(redPin, HIGH); digitalWrite(grnPin, LOW); digitalWrite(bluPin, LOW);
    printOutput(potVal, pot_state, distance_in, servo1_angle, servo2_angle);
}

void state1(int distance_in){
    pot_state = "Green Servo";
    // digitalWrite(redPin, LOW); digitalWrite(grnPin, HIGH); digitalWrite(bluPin, LOW);
    moveServo(servo1, distance_in, servo1_angle, servo1_lastUpdate);
    printOutput(potVal, pot_state, distance_in, servo1_angle, servo2_angle);
}

void state2(int distance_in) {
    pot_state = "Blue Servo";
    // digitalWrite(redPin, LOW); digitalWrite(grnPin, LOW); digitalWrite(bluPin, HIGH);
    moveServo(servo2, distance_in, servo2_angle, servo2_lastUpdate);
    printOutput(potVal, pot_state, distance_in, servo1_angle, servo2_angle);
}