#!/bin/bash
ffmpeg -f v4l2 -framerate 24 -video_size 640x480 -i /dev/video0 -f mpegts udp://192.168.0.21:1235