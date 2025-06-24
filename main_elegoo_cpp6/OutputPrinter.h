#ifndef OUTPUT_PRINTER_H
#define OUTPUT_PRINTER_H

#include <Arduino.h>

class OutputPrinter {
private:
  unsigned long lastPrintTime;
  unsigned long interval;

public:
  OutputPrinter(unsigned long updateInterval = 500)
    : lastPrintTime(0), interval(updateInterval) {}

  void json_print(int distance_in, int &left_motor_speed, int &right_motor_speed, unsigned long current_time);
};

#endif
