import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import radians, cos, sin
from matplotlib.colors import ListedColormap

# Dummy Data Example (Replace this with your actual CSV load)
data = {
    'F_USS': [109, 109, 28, 109, 28],
    'L_USS': [0, 0, 0, 0, 0],
    'R_USS': [31, 31, 31, 31, 31],
    'L_ENCD_COV': [0, 10, 20, 30, 40],
    'R_ENCD_COV': [0, 10, 20, 30, 40],
    'HEAD': [180, 180, 180, 180, 180]
}
#df = pd.DataFrame(data)
df = pd.read_csv("../plots_8_4/drive_3.csv")
# USS Max Range (in inches)
USS_MAX_RANGE = 100

# Grid setup
map_size_in = 1000
grid_size = int(map_size_in)
grid = np.full((grid_size, grid_size), 2)  # 2 = unknown
origin = grid_size // 2

x, y = 0, 0
path_x, path_y = [origin], [origin]

UNKNOWN = 2
FREE = 1
OBSTACLE = 0

def mark_grid_block(px, py, val, block_size=3):
    gx = int(round(px)) + origin
    gy = int(round(py)) + origin
    for dx in range(-block_size, block_size + 1):
        for dy in range(-block_size, block_size + 1):
            nx = gx + dx
            ny = gy + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                grid[ny, nx] = val

def clear_block_beam(rx, ry, theta_rad, distance_in):
    beam_reach = int(distance_in)
    for i in range(1, beam_reach):
        cx = rx + i * cos(theta_rad)
        cy = ry + i * sin(theta_rad)
        mark_grid_block(cx, cy, FREE)
    # Only mark obstacle if USS detected something within range
    if distance_in < USS_MAX_RANGE:
        ex = rx + beam_reach * cos(theta_rad)
        ey = ry + beam_reach * sin(theta_rad)
        mark_grid_block(ex, ey, OBSTACLE)

for i in range(1, len(df)):
    d = ((df.loc[i, 'L_ENCD_COV'] + df.loc[i, 'R_ENCD_COV']) / 2) - ((df.loc[i-1, 'L_ENCD_COV'] + df.loc[i-1, 'R_ENCD_COV']) / 2)
    heading_deg = df.loc[i, 'HEAD']
    theta = radians(90 - heading_deg)

    # Update robot position
    x += d * cos(theta)
    y += d * sin(theta)
    path_x.append(x + origin)
    path_y.append(y + origin)

    # USS clearing with obstacle marking logic
    clear_block_beam(x, y, theta, df.loc[i, 'F_USS'])
    clear_block_beam(x, y, theta + radians(90), df.loc[i, 'L_USS'])
    clear_block_beam(x, y, theta - radians(90), df.loc[i, 'R_USS'])

# Custom colormap: Obstacles (black), Free (white), Unknown (gray)
cmap = ListedColormap(['black', 'white', 'gray'])

# Plotting
plt.figure(figsize=(12, 6))
plt.imshow(grid, cmap=cmap, origin='lower', extent=[-origin/12, (grid_size-origin)/12, -origin/12, (grid_size-origin)/12])
plt.scatter([(px - origin)/12 for px in path_x], [(py - origin)/12 for py in path_y], c='red', s=5, label='Center Path', zorder=3)
plt.scatter((path_x[0] - origin)/12, (path_y[0] - origin)/12, c='green', s=30, label='Start', zorder=3)
plt.scatter((path_x[-1] - origin)/12, (path_y[-1] - origin)/12, c='blue', s=30, label='End', zorder=3)
plt.title("Block-based Occupancy Grid with Valid Obstacle Marking")
plt.xlabel("X (feet)")
plt.ylabel("Y (feet)")
plt.legend()
plt.show()
