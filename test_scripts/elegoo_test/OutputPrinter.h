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

  int mssg_id;

  void json_print(int motor_pwm, unsigned long current_time);
};

#endif
