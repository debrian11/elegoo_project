# Let's send you the actual code you need, no placeholder nonsense. Here is a complete USS occupancy grid code template.
# You will paste your CSV load in place of the dummy DataFrame.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import radians, cos, sin

# Replace this with your actual CSV path
# df = pd.read_csv("../plots_8_4/drive_3.csv")

# Dummy Data Example (REPLACE THIS with your CSV)
data = {
    'F_USS': [109, 109, 28, 109, 28],
    'L_USS': [0, 0, 0, 0, 0],
    'R_USS': [31, 31, 31, 31, 31],
    'L_ENCD_COV': [0, 5, 10, 15, 20],
    'R_ENCD_COV': [0, 5, 10, 15, 20],
    'HEAD': [180, 181, 182, 183, 184]
}
#df = pd.DataFrame(data)

df = pd.read_csv("../plots_8_4/drive_3.csv")
# Grid setup
map_size_in = 1000
grid_size = int(map_size_in)
grid = np.full((grid_size, grid_size), 2)  # 2 = unknown
origin = grid_size // 2

x, y = 0, 0
path_x, path_y = [origin], [origin]

def mark_grid(px, py, val):
    gx = int(round(px)) + origin
    gy = int(round(py)) + origin
    if 0 <= gx < grid_size and 0 <= gy < grid_size:
        grid[gy, gx] = val

def clear_uss_beam(rx, ry, theta_rad, dist):
    for i in range(1, int(dist)):
        cx = rx + i * cos(theta_rad)
        cy = ry + i * sin(theta_rad)
        mark_grid(cx, cy, 1)  # Free space
    # Optional: mark endpoint as obstacle (if you want to visualize that)
    # ex = rx + dist * cos(theta_rad)
    # ey = ry + dist * sin(theta_rad)
    # mark_grid(ex, ey, 0)  # Obstacle

for i in range(1, len(df)):
    d = ((df.loc[i, 'L_ENCD_COV'] + df.loc[i, 'R_ENCD_COV']) / 2) - ((df.loc[i-1, 'L_ENCD_COV'] + df.loc[i-1, 'R_ENCD_COV']) / 2)
    heading_deg = df.loc[i, 'HEAD']
    theta = radians(90 - heading_deg)

    # Update robot position
    x += d * cos(theta)
    y += d * sin(theta)
    path_x.append(x + origin)
    path_y.append(y + origin)

    # Clear USS beams
    clear_uss_beam(x, y, theta, df.loc[i, 'F_USS'])
    clear_uss_beam(x, y, theta + radians(90), df.loc[i, 'L_USS'])
    clear_uss_beam(x, y, theta - radians(90), df.loc[i, 'R_USS'])

# Plot
plt.figure(figsize=(12, 6))
plt.imshow(grid, cmap='gray_r', origin='lower', extent=[-origin/12, (grid_size-origin)/12, -origin/12, (grid_size-origin)/12])
plt.scatter([(px - origin)/12 for px in path_x], [(py - origin)/12 for py in path_y], c='red', s=5, label='Center Path')
plt.scatter((path_x[0] - origin)/12, (path_y[0] - origin)/12, c='green', s=30, label='Start')
plt.scatter((path_x[-1] - origin)/12, (path_y[-1] - origin)/12, c='blue', s=30, label='End')
plt.title("Occupancy Grid with USS Clearing")
plt.xlabel("X (feet)")
plt.ylabel("Y (feet)")
plt.legend()
plt.show()
