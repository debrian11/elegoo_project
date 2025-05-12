import time
import serial
import serial.tools.list_ports

# Get a list of all serial ports
ports = list(serial.tools.list_ports.comports())
arduino_port = None

# Assign the usbport # to the variable created above
for port in ports:
#    if 'usbmodem' in port.device:
    if 'cu.usbserial' in port.device:
        arduino_port = port.device
        print(f"Arduino connected to port {arduino_port}")
        break

# If port is valid, connect to the arduino serial port
if arduino_port != None:
    arduino = serial.Serial(port=arduino_port, baudrate=9600, timeout=1)
    time.sleep(2) # 2 seconds allows Arduino to initialize serial comms

    # While port is valid, send serial commands
    while arduino_port != None:
        user_input = input("Enter 'f (fwd)', 'b (bwd)', 's (stop)': ")

        # Allow user to enter cmd to exit
        if user_input.lower() == 'exit': # .lower converts the input to lowercase
            break

        # Write user input over the serial
        arduino.write((user_input.lower() + '\n').encode('utf-8'))
        time.sleep(0.1)

else:
    print("no USB serial device detected")
