#!/bin/bash

# Wait until both Arduinos are connected
#while [ ! -e /dev/arduino_elegoo ] || [ ! -e /dev/arduino_nano ]; do

nano_port="/dev/arduino_nano"
elegoo_port="/dev/arduino_elegoo"
script_path="/opt/scripts"
script_name="pi_serial_json_4.0.0.0.py"


while [ ! -e $nano_port ] && [ ! -e $elegoo_port ]; do
	echo "Waiting for Arduino Connection"

	if [ ! -e $nano_port] && [ -e $elegoo_port]; then
		echo "Elegoo connected. Waiting for Nano connection"
	
	elif [ -e $nano_port] && [ ! -e $elegoo_port]; then
		echo "Nano connect. Waiting for Elegoo"
	fi
done

#Run script to begin Arduino / Mac comms
echo "Starting script"
python3 $script_path/$script_name
