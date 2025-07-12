// Setup scripts for the motors, servo, ultrasonicsensor
void setupMotors() {
    pinMode(PWMA, OUTPUT);
    pinMode(AIN1, OUTPUT);

    pinMode(PWMB, OUTPUT);
    pinMode(BIN1, OUTPUT);

    pinMode(STBY, OUTPUT);
    digitalWrite(STBY, HIGH);  // Enable motors
}

void setupServo() {
    servo1.attach(servo1_pin);
    servo2.attach(servo2_pin);
}
