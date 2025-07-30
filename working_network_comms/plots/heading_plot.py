import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('nano_log.csv')

# Normalize time
df['relative_time'] = df['timestamp'] - df['timestamp'].iloc[0]

# Convert heading from degrees to radians
df['heading_rad'] = np.deg2rad(df['HEAD'])

# Scale time into radius just to give spacing on the polar plot
r = df['relative_time']
theta = df['heading_rad']

plt.figure(figsize=(8, 8))
ax = plt.subplot(111, projection='polar')
ax.set_theta_direction(-1)  # Make angle increase clockwise
ax.set_theta_zero_location("N")  # Make 0° point upward

ax.plot(theta, r, color='purple', linewidth=1)
ax.set_title("Heading Evolution Over Time", va='bottom')
ax.set_rlabel_position(-22.5)  # Move radius labels
plt.show()
