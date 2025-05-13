#include "LEDController.h"
#include <Arduino.h>  // Needed for pinMode, digitalWrite

// Constructor: runs when you create an LEDController object
LEDController::LEDController(int pinNumber) {
  ledPin = pinNumber;             // Save the pin number
  pinMode(ledPin, OUTPUT);        // Set the pin to output mode
  //Serial.begin(9600);
}

// Turns the LED on
void LEDController::turnOn() {
  digitalWrite(ledPin, HIGH);
}

// Turns the LED off
void LEDController::turnOff() {
  digitalWrite(ledPin, LOW);
}

// Turns the LED on and off
void LEDController::blinker() {
  digitalWrite(ledPin, HIGH);
  Serial.println("On");
  delay(500);
  digitalWrite(ledPin, LOW);
  Serial.println("Off");
  delay(500);
}