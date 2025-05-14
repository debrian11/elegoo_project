#include "LEDController.h"

LEDController myLED1(11);
LEDController myLED2(10);
LEDController myLED3(9);


/*
LEDController myLED1;
LEDController myLED2;
LEDController myLED3;
*/

void setup() {
  Serial.begin(9600);
  /*
  myLED1.attach(11);
  myLED2.attach(10);
  myLED3.attach(9);
  */
}

void loop() {
  myLED1.blinker();
  myLED2.blinker();
  myLED3.turnOn();
}
