// -------- Servo commands
void moveServo(Servo &servo, int distance_in, int &angle_store, unsigned long &lastUpdate) {
  const unsigned long servo_interval = 50;  // update every 50 ms
  int target_angle = angle_store;

  if (current_time - lastUpdate < servo_interval) return;
  lastUpdate = current_time;

  if (distance_in < 2 || distance_in > max_dist) return; // Don't move servo if sensor too close / too far

  if (distance_in >= 2 && distance_in <= 6) {
    target_angle = 120;
  } else if (distance_in > 8) {
    target_angle = 90;
  }

  if (target_angle != angle_store) {
    servo.write(target_angle);
    angle_store = target_angle;
  }
}