import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
import datetime

# colors = ["#FF0000", "#00A08A", "#F2AD00", "#F98400", "#5BBCD6"]
colors = ["#FF0000", "#00A08A", "#F98400", "#5BBCD6"]
labels = [
    "Hallway", # Sensor 1 - 
    "Kitchen", # Sensor 2 - 
    "Bed room", # Sensor 3 - 
    "Back room / office", # Sensor 4 - 
]

with open("datapoints.csv", "r") as datafile:
    filecontents = datafile.readlines()

# Remove carriage returns
# Split on comma
filecontents = [f.strip("\n").split(",") for f in filecontents]

# Save headers
headers = np.array(filecontents[0])

# Save values and convert to integers
# Use transpose, each index of datapoints is a timeseries of each channel
datapoints = np.array(filecontents[1:], dtype=int)
datapoints = datapoints.T

# Parse the data into float-type arrays for post processing
timestamps = datapoints[0]
temps = np.array(datapoints[1:5], dtype=float)
hums = np.array(datapoints[5:9], dtype=float)
batts = np.array(datapoints[9:13], dtype=float)

# Convert timestamps to dates
dates = [datetime.datetime.fromtimestamp(ts/1e3) for ts in timestamps]

# Convert temperature from Celsius to Fahrenheit
temps = temps / 10.0
temps = temps * (9.0/5.0) + 32

# Humidity are multiplied by 10 and stored as ints on the sensor
hums = hums / 10.0

fig, ax_list = plt.subplots(
    3, 1,
    sharex=True,
    figsize=(10, 8),
    gridspec_kw={'height_ratios': [3, 3, 2]}
)

ax_list = ax_list.flatten()
for ax in ax_list:
    ax.grid()

for i in range(4):
    ax_list[0].plot(dates, temps[i], '-o', ms=4, color=colors[i], label=labels[i])
ax_list[0].set_ylabel("Temperature (F)")

for i in range(4):
    ax_list[1].plot(dates, hums[i], '-o', ms=4, color=colors[i], label=labels[i])
ax_list[1].set_ylabel("Humidity (%)")

for i in range(4):
    ax_list[2].plot(dates, batts[i], '-o', ms=4, color=colors[i], label=labels[i])
ax_list[2].set_ylabel("Battery level")
ax_list[2].legend(loc="lower left")
xfmt = md.DateFormatter('%m/%d/%y %H:%M')
ax_list[2].xaxis.set_major_formatter(xfmt)
ax_list[2].tick_params(axis="x", rotation=70)

plt.show()
