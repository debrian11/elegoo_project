# This scripts streams the webcam video at the /dev/usb0 over UDP
import subprocess


def pi_video_stream():
    stream_process = subprocess.Popen([
        "ffmpeg",
        "-f", "v4l2",
        "-framerate", "24",
        "-video_size", "640x800",
        "-i", "/dev/video0",
        "-f", "mpegts",
        "udp://192.168.0.21:1235"
    ])
    return stream_process