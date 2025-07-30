import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import radians, cos, sin

# Load your log file
df = pd.read_csv("nano_log_7_20.csv")

# Calculate DIST if not already
df['DIST'] = (df['L_ENCD_COV'] + df['R_ENCD_COV']) / 2

# Map grid setup
map_size_in = 100  # 100x100 inches
cell_size = 1      # 1 inch per cell
grid_size = int(map_size_in / cell_size)
grid = np.full((grid_size, grid_size), 2)  # 2 = occupied

origin = grid_size // 2  # (0,0) at center of grid
x, y = 0, 0               # robot starts at center
path_x, path_y = [origin], [origin]

# Robot body size
robot_radius = 3  # inches (6" total width)

# Function to mark robot's footprint as free
def mark_robot_area(gx, gy, radius_in_cells):
    for dx in range(-radius_in_cells, radius_in_cells + 1):
        for dy in range(-radius_in_cells, radius_in_cells + 1):
            if dx**2 + dy**2 <= radius_in_cells**2:
                px = gx + dx
                py = gy + dy
                if 0 <= px < grid_size and 0 <= py < grid_size:
                    grid[py, px] = 1  # 1 = free space

# Walk through each step
for i in range(1, len(df)):
    d = df.loc[i, 'DIST'] - df.loc[i - 1, 'DIST']
    heading_deg = df.loc[i, 'HEAD']
    theta = radians(heading_deg)

    # Update robot center position
    x += d * cos(theta)
    y += d * sin(theta)

    # Convert to grid cell coordinates
    gx = int(round(x)) + origin
    gy = int(round(y)) + origin

    if 0 <= gx < grid_size and 0 <= gy < grid_size:
        mark_robot_area(gx, gy, radius_in_cells=int(robot_radius))
        path_x.append(gx)
        path_y.append(gy)

# Plot the map
plt.figure(figsize=(8, 8))
plt.imshow(grid, cmap='gray_r', origin='lower')
#plt.plot(path_x, path_y, 'r--', label='Robot Path')
plt.scatter(path_x, path_y, c='red', s=3, label='Center Path')
plt.scatter(path_x[0], path_y[0], c='green', label='Start')
plt.scatter(path_x[-1], path_y[-1], c='blue', label='End')
plt.title("Occupancy Grid with Robot Footprint (6\" Wide)")
plt.xlabel("X (inches)")
plt.ylabel("Y (inches)")
plt.legend()
plt.grid(False)
plt.show()
