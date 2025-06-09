#!/bin/bash
# smaller

libcamera-vid -t 0 \
--width 1920 --height 1080 \
--codec h264 --framerate 24 --inline \
--profile baseline --level 4.1 \
--bitrate 6000000 -o - | \
ffmpeg -f h264 -i - -f mpegts udp://192.168.0.21:1234
