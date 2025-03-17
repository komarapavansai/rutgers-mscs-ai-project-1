import matplotlib.pyplot as plt
import csv
import numpy as np
from scipy.interpolate import CubicSpline
from collections import defaultdict

# Initialize a dictionary to store lists of y-values for each x-value
x_to_y = defaultdict(list)

# Read CSV data and filter for 'bot1'
with open('graph_data_bot2.csv', mode='r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header
    for row in reader:
        if row[3] == 'bot2':  # Check the label to identify the bot
            x_val = float(row[1])  # Assuming the second column is x
            y_val = float(row[0])  # Assuming the first column is y
            x_to_y[x_val].append(y_val)  # Group y-values by x-value

# Calculate the average y-value for each x
x_vals_avg = []
y_vals_avg = []

for x_val, y_vals in x_to_y.items():
    avg_y = sum(y_vals) / len(y_vals)  # Calculate the average of y-values for this x
    x_vals_avg.append(x_val)
    y_vals_avg.append(avg_y)

# Sorting the x values and their corresponding y values
sorted_x_vals_avg = sorted(x_vals_avg)
sorted_y_vals_avg = [y_vals_avg[x_vals_avg.index(x)] for x in sorted_x_vals_avg]

# Create a cubic spline interpolation for the smooth curve
cs = CubicSpline(sorted_x_vals_avg, sorted_y_vals_avg)

# Create a range of x values to get a smooth curve
x_smooth = np.linspace(min(sorted_x_vals_avg), max(sorted_x_vals_avg), 500)
y_smooth = cs(x_smooth)

# Plotting the original data points (averaged)
plt.scatter(sorted_x_vals_avg, sorted_y_vals_avg, c='blue', label='bot2')

# Plot the smooth curve
plt.plot(x_smooth, y_smooth, c='red', label='Cubic Spline Curve', linewidth=2)

plt.xlabel('q (flammability)')
plt.ylabel('Average frequency of success')
plt.title('Graph for bot2 success')

# Show the plot
plt.legend()
plt.show()
