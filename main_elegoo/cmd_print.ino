// -------- Serial output
void printOutput(int potVal, String pot_state, int distance_in, int &servo_angle, int &servo_angle2) {
    unsigned long print_interval = 500;  // update every 50 ms
    
    if (current_time - print_update >= print_interval) {
    print_update = current_time;
    Serial.print("potVal "); Serial.print(potVal);
    Serial.print(" | state: "); Serial.print(pot_state);
    Serial.print(" | in: "); Serial.print(distance_in);
    Serial.print(" | angle: "); Serial.print(servo1_angle);
    Serial.print(" | angle: "); Serial.println(servo2_angle);
  }
}