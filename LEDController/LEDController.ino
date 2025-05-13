#include "LEDController.h"

// Create an LED controller for pin 13
LEDController myLED1(11);
LEDController myLED2(10);
LEDController myLED3(9);

void setup() {
  Serial.begin(9600);
}

void loop() {
  myLED1.blinker();
  myLED2.blinker();
  myLED3.turnOn();
}
