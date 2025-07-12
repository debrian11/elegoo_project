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

  void json_print(int left_encoder, int right_encoder, unsigned long current_time);
  int mssg_id = 0;
};

#endif
