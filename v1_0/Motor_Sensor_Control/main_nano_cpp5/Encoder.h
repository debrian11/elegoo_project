#ifndef ENCODER_COUNT_H
#define ENCODER_COUNT_H

#include <Arduino.h>

void encoder_setup(int leftPin, int rightPin);
void leftISR();
void rightISR();

unsigned long getLeftEncoder();
unsigned long getRightEncoder();

#endif
