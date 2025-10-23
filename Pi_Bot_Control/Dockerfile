# Dockerfile
FROM python:3.11-slim

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# App directory
WORKDIR /opt/

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Project files
COPY pi_serial_json_8.0.0.0.py \
    heading_module.py \
    network_module.py \
    parsing_modules.py \
    pi_stream_video_usb.py \
    serial_module.py \
    uss_functions.py \
    /opt/scripts/

# CSV folder for data logging from scripts
RUN mkdir -p /opt/scripts/csv_files

ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "/opt/scripts/pi_serial_json_8.0.0.0.py"]