#ifndef OUTPUT_PRINTER_H
#define OUTPUT_PRINTER_H

#include <Arduino.h>
#include "Motorcontroller.h"
#include "Servo_custom.h"

class OutputPrinter {
private:
  unsigned long lastPrintTime;
  unsigned long interval;

public:
  OutputPrinter(unsigned long updateInterval = 500)
    : lastPrintTime(0), interval(updateInterval) {}

  int mssg_id;

  void json_print(int distance_in, MotorController &motor, Servo_custom &servo, unsigned long current_time);
};

#endif
