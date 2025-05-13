#ifndef LED_CONTROLLER_H
#define LED_CONTROLLER_H

class LEDController {
public:
  LEDController(int pinNumber);   // Constructor: sets up which pin the LED is on
  void turnOn();                  // Function to turn the LED on
  void turnOff();                 // Function to turn the LED off
  void blinker();                 // Function to make it blink

private:
  int ledPin;                     // Private variable: stores the pin number
};

#endif
