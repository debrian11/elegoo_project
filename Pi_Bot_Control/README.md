# Pi Overview

**Updated 12/17/2025**    
## Version 2.0
Currently in work.
Aim is to make code base more easily testable and modular through cleaner coding structure now that general bot functionality is determined.
Goals:
- Refactor Pi Control python scripts.
- Allow open loop testing feedback by injecting logged CSV data from previous known good bot runs to test code without needing pi.
- Add heart beat monitor between control laptop and 2nd pi
- Pass mapping data to 2nd pi
- Add navigation commands from control laptop


## Version 1.0
The main python script is the *pi_serial_json_x.x.py*. All other .py scripts are used as helper scripts and functions.  
The Docker file creates a contain with those scripts so that Pi functions can easily be deployed to additional Pi's as needed.  
The container itself is ran with docker compose. In the future, the service file will actually be running upon every reboot vs just docker compose up everytime to run the script.  