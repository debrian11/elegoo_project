
import json

stop_cmd =  { "L_DIR": 1, "R_DIR": 1, "L_PWM": 0, "R_PWM": 0 }
a = json.dumps(stop_cmd)
print(a)
b = json.loads(a)