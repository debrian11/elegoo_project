FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 python3-tk ffmpeg x11-apps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY mac_gui_7.0.0.0.py .

CMD ["python3", "mac_gui_7.0.0.0.py"]
