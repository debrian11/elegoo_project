#!/bin/bash
name="pi_brain"
version="1.0.0"
container_name="pi_brain.tar"

echo "Running the container"
podman run --name pi_bot \
    --restart=always -d \
    --network=host \
    --device /dev/arduino_elegoo:/dev/arduino_elegoo \
    --device /dev/arduino_nano:/dev/arduino_nano \
    -v /opt/scripts/csv_files:/opt/scripts/csv_files \
    $name:$version

echo "List running containers"
podman ps

