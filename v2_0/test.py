import json

buffer = '{"mssg_id":993,"F_USS":12,"L_USS":16,"R_USS":89,"L_ENCD":315,"R_ENCD":52}\n'

line, buffer = buffer.split("\n", 1)
print(len(line))
print(line)
line = line.strip()
print(len(line))
print(line)
line += ""
print(len(line))
print(line)
