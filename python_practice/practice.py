#------------ for loop --------------#
# sensor = { "type": "ultrasonic", "distance": 30 }
#for random in sensor:
#    print(random, sensor[random])

{
  "battery": 7.9,
  "obstacles": [0, 1, 0, 1]
}

data = {
  "obstacles": [0, 1, 0, 1, 5, 6, 7, 8]
}

""""
print(data)
for i, val in enumerate(data["obstacles"]):
    #print("Sensor", i, "saw", "something" if val else "nothing")
    print(i, val)
"""

numbers = {
    "set1": [5, 10, 15],
    "set2": [6, 12, 18]
}


sensor_val = 7
motion_val = "fwd"
servo_val = "sweep"

datastuff = {
    "distance": [sensor_val],
    "motion": [motion_val],
    "servo": [servo_val]
}

#for a, b in enumerate(datastuff["motion"]):
#    print(a, b)

#for a in datastuff["motion"], datastuff["distance"], datastuff["servo"]:
#    print(a)



#commands = ["forward", "left", "left", "stop"]
#for i, cmd in enumerate(commands):
    #print(f"[{i}] Executing: {cmd}")
    #print([{i}], "Executing: {cmd}")
#    print(f"{i} {cmd}")

#------------- print f ---------------#
#otor = "FORWARD"
#speed = 80
#print(f"Motor direction: {motor}, Speed: {speed}")


#try:
#    num = int("hello")
#except:
#    print("Conversion failed")

#try:
###    x = int(input("Enter a number: "))
#    result = 100 / x
  #  print("Result is", result)
#except ZeroDivisionError:
#    print("Can't divide by zero.")
#except ValueError:
#    print("That's not a number.")


#try:
#    file = open("robot_config.txt", "r")
#    data = file.read()
#    print(data)
#    file.close()
#except:
#    print("no file")


msg = '{"motor": "FORWARD", "servo": "S_STOP", "battery": 7.8}'
