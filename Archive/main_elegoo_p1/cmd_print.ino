// -------- Serial output
String motorStateToString(motorstate_t state) {
  switch(state) {
      case FORWARD: return "FORWARD";
      case BACKWARD: return "BACKWARD";
      case STOP: return "STOP";
      default: return "UNKNOWN";
  }
}

void printOutput(int distance_in) {
  unsigned long print_interval = 500;  // update every x ms
  
  if (current_time - print_update >= print_interval) {
      print_update = current_time;
      Serial.print("in: "); Serial.print(distance_in);
      Serial.print(" | MotorState: "); Serial.println(motorStateToString(currentmotorstate));
  }
}
