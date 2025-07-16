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

  int mssg_id = 0;

  void json_print(int front_sensor, int left_sensor, int right_sensor, 
                  int left_encoder, int right_encoder, int mag_meter, 
                  unsigned long current_time);
};

#endif
