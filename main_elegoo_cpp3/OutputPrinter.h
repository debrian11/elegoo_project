#ifndef OUTPUT_PRINTER_H
#define OUTPUT_PRINTER_H

#include <Arduino.h>

enum motorstate_t { FORWARD, BACKWARD, STOP, LEFT, RIGHT };

class OutputPrinter {
private:
  unsigned long lastPrintTime;
  unsigned long interval;

public:
  OutputPrinter(unsigned long updateInterval = 100)
    : lastPrintTime(0), interval(updateInterval) {}
  void print(int distance_in, motorstate_t currentState, unsigned long current_time);
  String motorStateToString(motorstate_t state);
};

#endif
