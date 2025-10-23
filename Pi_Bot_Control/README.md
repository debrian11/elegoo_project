# Pi Overview

**Updated 10/22/2025**    
The main python script is the *pi_serial_json_x.x.py*. All other .py scripts are used as helper scripts and functions.  
The Docker file creates a contain with those scripts so that Pi functions can easily be deployed to additional Pi's as needed.  
The container itself is ran with docker compose. In the future, the service file will actually be running upon every reboot vs just docker compose up everytime to run the script.  