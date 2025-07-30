import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from math import radians, cos, sin

# Load CSV
df = pd.read_csv("nano_log_mod.csv")

# Convert timestamps to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

# Resample to ~0.5 second intervals
df_resampled = df.set_index('timestamp').resample('500ms').first().dropna().reset_index()

# Calculate average encoder-based distance (inches assumed)
df_resampled['DIST'] = (df_resampled['L_ENCD_COV'] + df_resampled['R_ENCD_COV']) / 2

# Initialize storage
center_points = []
left_edges = []
right_edges = []

# Build corridor shape
for i in range(1, len(df_resampled)):
    d = df_resampled.loc[i, 'DIST'] - df_resampled.loc[i - 1, 'DIST']
    heading_deg = df_resampled.loc[i, 'HEAD']
    theta = radians(heading_deg)

    # Calculate robot's center point
    x_c = center_points[-1][0] + d * cos(theta) if center_points else 0
    y_c = center_points[-1][1] + d * sin(theta) if center_points else 0
    center_points.append((x_c, y_c))

    # USS sensor values (cm to meters)
    l_dist = df_resampled.loc[i, 'L_USS'] / 100
    r_dist = df_resampled.loc[i, 'R_USS'] / 100

    # Calculate left/right wall points using heading
    left_theta = radians(heading_deg + 90)
    right_theta = radians(heading_deg - 90)

    x_l = x_c + l_dist * cos(left_theta)
    y_l = y_c + l_dist * sin(left_theta)
    x_r = x_c + r_dist * cos(right_theta)
    y_r = y_c + r_dist * sin(right_theta)

    left_edges.append((x_l, y_l))
    right_edges.append((x_r, y_r))

# Build polygon patches between wall edges
patches = []
for i in range(1, len(left_edges)):
    poly = Polygon([left_edges[i-1], left_edges[i], right_edges[i], right_edges[i-1]], closed=True)
    patches.append(poly)

# Plot
fig, ax = plt.subplots(figsize=(10, 10))
p = PatchCollection(patches, facecolor='gray', alpha=0.5, edgecolor='black')
ax.add_collection(p)

# Plot path
x_c, y_c = zip(*center_points)
ax.plot(x_c, y_c, 'k--', label='Robot Path')

ax.set_aspect('equal')
ax.set_xlabel("X (meters)")
ax.set_ylabel("Y (meters)")
ax.set_title("Corridor Map with Width from USS Sensors")
ax.legend()
plt.grid(True)
#plt.xlim(40, 60)   # adjust as needed to zoom in
#plt.ylim(-40, -60)   # adjust as needed to zoom in
plt.show()
