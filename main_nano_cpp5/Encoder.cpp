#include "Encoder.h"

volatile unsigned long left_encoder_count = 0;
volatile unsigned long right_encoder_count = 0;
int left_pin, right_pin;

void leftISR() {
  left_encoder_count++;
}

void rightISR() {
  right_encoder_count++;
}

void encoder_setup(int lPin, int rPin) {
  left_pin = lPin;
  right_pin = rPin;

  pinMode(left_pin, INPUT_PULLUP);
  pinMode(right_pin, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(left_pin), leftISR, FALLING);
  attachInterrupt(digitalPinToInterrupt(right_pin), rightISR, FALLING);
}

unsigned long getLeftEncoder() {
  return left_encoder_count;
}

unsigned long getRightEncoder() {
  return right_encoder_count;
}
