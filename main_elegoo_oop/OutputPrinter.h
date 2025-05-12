#ifndef OUTPUT_PRINTER_H
#define OUTPUT_PRINTER_H

enum motorstate_t { FORWARD, BACKWARD, STOP, LEFT, RIGHT };

class OutputPrinter {
private:
  unsigned long lastPrintTime;
  unsigned long interval;

public:
  OutputPrinter(unsigned long updateInterval = 100)
    : lastPrintTime(0), interval(updateInterval) {}

  String motorStateToString(motorstate_t state) {
    switch (state) {
      case FORWARD: return "FORWARD";
      case BACKWARD: return "BACKWARD";
      case STOP: return "STOP";
      case LEFT: return "LEFT";
      case RIGHT: return "RIGHT";
      default: return "UNKNOWN";
    }
  }

  void print(int distance_in, motorstate_t currentState, unsigned long current_time) {
    if (current_time - lastPrintTime >= interval) {
      lastPrintTime = current_time;
      Serial.print("in: "); Serial.print(distance_in);
      Serial.print(" | MotorState: "); Serial.println(motorStateToString(currentState));
    }
  }
};

#endif
