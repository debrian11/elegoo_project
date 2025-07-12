void serial_check() {
    if (Serial.available() > 0) {
        String serial_input = Serial.readStringUntil('\n');
        serial_input.trim();
    
        if (serial_input == "f") {
            currentmotorstate = FORWARD;
        } else if (serial_input == "b") {
            currentmotorstate = BACKWARD;
        } else if (serial_input == "stop") {
            currentmotorstate = STOP;
        }
    }
}
