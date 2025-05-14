#include "LEDController_timing.h"
#include <Arduino.h>  // Needed for pinMode, digitalWrite

// Constructor: runs when you create an LEDController object

LEDController::LEDController(int pinNumber) {
  ledPin = pinNumber;             // Save the pin number
  pinMode(ledPin, OUTPUT);        // Set the pin to output mode
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
  //Serial.println("On");
  delay(500);
  digitalWrite(ledPin, LOW);
  //Serial.println("Off");
  delay(500);
}

void LEDController::blinker_millis() {
  unsigned long current_time = millis();

  if (current_time - last_led_update >= 500) {
    last_led_update = current_time;

    if (digitalRead(ledPin) == HIGH) {
      digitalWrite(ledPin, LOW);
      Serial.println("Off");
    } else {
      digitalWrite(ledPin, HIGH);
      Serial.println("On");
    }
  }
}

void LEDController::blinker_millis_og() {
  unsigned long current_time = millis();
  if (current_time - last_led_update >= 1000) {
      digitalWrite(ledPin, HIGH);
      last_led_update = current_time;
      Serial.println("On");
  } else {
    digitalWrite(ledPin, LOW);
    Serial.println("Off");
  }
}