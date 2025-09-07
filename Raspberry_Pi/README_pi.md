# Raspberry Pi Code Summary

## **Core Purpose**

Acts as the central bridge:

* **Serial read/write** with Arduino
* **TCP socket server** for Mac
* **Streams USB camera video via UDP** to the Mac

### 🔧 Files:

#### `pi_serial_json.py`

* Detects Arduino automatically via `serial.tools.list_ports`
* Opens TCP socket on port `9000`
* Starts video streaming via `ffmpeg` (calls `pi_stream_video_usb`)
* Loop:

  * Read Arduino JSON telemetry
  * Forward to Mac
  * Receive Mac commands
  * Forward to Arduino

#### `pi_stream_video_usb.py`

* Launches a UDP `ffmpeg` stream from `/dev/video0` to Mac IP `192.168.0.21:1235`