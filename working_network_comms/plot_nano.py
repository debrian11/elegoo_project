import pandas as pd
import matplotlib.pyplot as plt

# Load your CSV
df = pd.read_csv("nano_log.csv")

# Optional: convert timestamp to relative time
df['timestamp'] = df['timestamp'] - df['timestamp'].iloc[0]

# Plot USS readings
plt.figure()
plt.plot(df['timestamp'], df['F_USS'], label='Front USS')
plt.plot(df['timestamp'], df['L_USS'], label='Left USS')
plt.plot(df['timestamp'], df['R_USS'], label='Right USS')
plt.xlabel("Time (s)")
plt.ylabel("Distance (cm)")
plt.title("Ultrasonic Sensor Readings Over Time")
plt.legend()
plt.grid(True)
plt.show()

# Plot encoder counts
plt.figure()
plt.plot(df['timestamp'], df['L_ENCD'], label='Left Encoder')
plt.plot(df['timestamp'], df['R_ENCD'], label='Right Encoder')
plt.xlabel("Time (s)")
plt.ylabel("Encoder Count")
plt.title("Encoder Readings Over Time")
plt.legend()
plt.grid(True)
plt.show()
