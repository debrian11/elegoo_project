import json

try:
    data = json.loads(msg)  # Now it's a Python dict!
    print(data["motor"])    # prints "FORWARD"
except json.JSONDecodeError:
    print("Bad JSON format")
