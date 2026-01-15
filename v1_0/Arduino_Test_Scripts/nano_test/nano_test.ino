// 09/02/2025
// This script outputs the json key value pairs the nano normally sends
#include "OutputPrinter.h"

unsigned long current_time;
unsigned long last_time_update = 0;
int heading = 0;
int f_uss = 1;
int r_uss = 2;
int l_uss = 3;
int l_encd = 4;
int r_encd = 5;


// Output
OutputPrinter serial_printer(500);

void setup() {
  Serial.begin(115200);
}

void loop() {
  current_time = millis();

// For test purposes only in simulating a changing distance output of Ultrasonic
  if (current_time - last_time_update > 110) {
    last_time_update = current_time;
    if (heading > 100) {
      heading = 0;
      f_uss = 1;
      r_uss = 2;
      l_uss = 3;
      l_encd = 4;
      r_encd = 5;
    } 
      heading += 3;
      f_uss += 2;
      r_uss += 2;
      l_uss += 2;
      l_encd += 5;
      r_encd += 5;
  }

  // Output the motor speed and Ultrasonic distance back
  serial_printer.json_print(f_uss, r_uss, l_uss, l_encd, r_encd, heading, current_time);
}
