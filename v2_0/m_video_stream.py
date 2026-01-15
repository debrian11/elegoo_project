# This scripts streams the webcam video at the /dev/usb0 over UDP
import subprocess

def pi_video_stream(usb_path: str, ip_out: str, port_out: int):
    stream_process = subprocess.Popen([
        "ffmpeg",
        "-f", "v4l2",
        "-framerate", "24",
        "-video_size", "640x800",
        "-i", usb_path,
        "-f", "mpegts",
        f"udp://{ip_out}:{port_out}"
    ])
    return stream_process


def video_ingest(ip_in: str, port_in: int):
    pass