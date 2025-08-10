import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import radians, cos, sin

# Load your log file
df = pd.read_csv("../plots_8_4/drive_3.csv")

# Calculate DIST if not already
ticks_per_inch = 9.25
#df['DIST'] = ((df['L_ENCD_COV'] + df['R_ENCD_COV']) / 2) / ticks_per_inch
df['DIST'] = ((df['L_ENCD_COV'] + df['R_ENCD_COV']) / 2)
#df['DIST'] = ((df['L_ENCD'] + df['R_ENCD']) / 2) / ticks_per_inch

# Compute max possible travel (bounding box)
max_distance = df['DIST'].max()  # in inches
# Add a buffer (e.g., 2 feet) so it's not cramped at the edge
buffer_in_inches = 24
map_size_in = int((max_distance + buffer_in_inches) * 2)  # *2 because robot can go negative too

# Map grid setup
#map_size_in = 1000  # 100x100 inches
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
    #theta = radians(heading_deg)
    theta = radians(90 - heading_deg) # converted from compass headings


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
# Compute path bounds (in feet)
path_x_feet = [(px - origin) / 12 for px in path_x]
path_y_feet = [(py - origin) / 12 for py in path_y]
#plt.imshow(grid, cmap='gray_r', origin='lower')
plt.imshow(grid, cmap='gray_r', origin='lower', extent=[
    -origin / 12, (grid_size - origin) / 12,
    -origin / 12, (grid_size - origin) / 12
])
plt.scatter(path_x_feet, path_y_feet, c='red', s=10, label='Center Path', zorder=3)
plt.scatter(path_x_feet[0], path_y_feet[0], c='green', s=30, label='Start', zorder=3)
plt.scatter(path_x_feet[-1], path_y_feet[-1], c='blue', s=30, label='End', zorder=3)

plt.title("Occupancy Grid with Robot Footprint (6\" Wide)")
plt.xlabel("X (feet)")
plt.ylabel("Y (feet)")
plt.legend()
plt.grid(False)

buffer_feet = 2  # feet of margin
plt.xlim(min(path_x_feet) - buffer_feet, max(path_x_feet) + buffer_feet)
plt.ylim(min(path_y_feet) - buffer_feet, max(path_y_feet) + buffer_feet)

plt.show()

