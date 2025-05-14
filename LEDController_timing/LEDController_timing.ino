#include "LEDController_timing.h"

LEDController myLED1(11);
LEDController myLED2(10);
LEDController myLED3(9);
unsigned long current_time;

void setup() {
  Serial.begin(9600);
}

void loop() {
  current_time = millis();
  //myLED1.blinker();
  //myLED2.blinker_millis_og();
  myLED3.blinker_millis();
}
