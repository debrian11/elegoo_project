// -------- Ultrasonic sensor reading
int read_us_sensor () {
  if (current_time - ultrasonic_last_update >= 50) {
    ultrasonic_last_update = current_time;
    int distance_cm = sonar.ping_cm();
    return distance_cm * 0.393701;
  }
}