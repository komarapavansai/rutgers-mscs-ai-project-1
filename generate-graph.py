import matplotlib.pyplot as plt
import csv
from collections import defaultdict

# Define the bot indices (for example: 1, 2, 3, 4)
bot_indices = [1, 2, 3, 4]

# Create a color map to differentiate the bots
colors = ['blue', 'green', 'red', 'purple']
bot_labels = ['bot1', 'bot2', 'bot3', 'bot4']

# Initialize a dictionary to store lists of y-values for each x-value for each bot
x_to_y = defaultdict(list)
# Loop through each bot's CSV file
for i, bot_index in enumerate(bot_indices):
    # Read CSV data for each bot
    # file_name = f'graph_data_bot{bot_index}.csv'
    file_name = f'./gd_bot{bot_index}.csv'
    # file_name = f'filtered_data.csv'
    with open(file_name, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 4:  # Check if row has enough columns
                if row[3] == bot_labels[i]:  # Check the label to identify the bot
                    x_val = float(row[1])  # Assuming the second column is x
                    y_val = float(row[0])  # Assuming the first column is y
                    x_to_y[bot_index].append((x_val, y_val))  # Group (x, y) pairs for each bot

# Calculate the average y-value for each x for each bot
x_vals_avg = []
y_vals_avg = []

for bot_index in bot_indices:
    # Group y-values by x-value for each bot
    x_to_y_bot = x_to_y[bot_index]
    
    # Calculate the average y-value for each unique x-value
    x_dict = defaultdict(list)
    for x_val, y_val in x_to_y_bot:
        x_dict[x_val].append(y_val)

    # Calculate the average y for each x
    for x_val, y_vals in x_dict.items():
        avg_y = sum(y_vals) / len(y_vals)  # Calculate the average of y-values for this x
        x_vals_avg.append(x_val)
        y_vals_avg.append(avg_y)

# Sorting the x values and their corresponding y values
sorted_x_vals_avg = sorted(x_vals_avg)
sorted_y_vals_avg = [y_vals_avg[x_vals_avg.index(x)] for x in sorted_x_vals_avg]

# Plotting the averaged data points
plt.figure(figsize=(10, 6))  # Make the figure bigger

# Iterate through each bot's data and plot
for i, bot_index in enumerate(bot_indices):
    bot_data = x_to_y[bot_index]
    if bot_data:
        # Group y-values by x for the current bot
        x_dict = defaultdict(list)
        for x_val, y_val in bot_data:
            x_dict[x_val].append(y_val)

        # Calculate the average y-value for each x
        avg_x_vals = []
        avg_y_vals = []
        for x_val, y_vals in x_dict.items():
            avg_y = sum(y_vals) / len(y_vals)
            avg_x_vals.append(x_val)
            avg_y_vals.append(avg_y)

        # Sort by x values
        sorted_avg_x_vals = sorted(avg_x_vals)
        sorted_avg_y_vals = [avg_y_vals[avg_x_vals.index(x)] for x in sorted_avg_x_vals]

        # Plot the average data points with the corresponding color and label
        plt.plot(sorted_avg_x_vals, sorted_avg_y_vals, c=colors[i], label=f'{bot_labels[i]}', linewidth=2)

# Adding labels and title
plt.xlabel('q (flammability)', fontsize=14)
plt.ylabel('Average frequency of success', fontsize=14)
# plt.title('Average success frequency of Bot3', fontsize=16)
plt.title('Average success frequency for all Bots)', fontsize=16)

# Set x-axis to start from 0 and adjust y-axis limits to start from 0 as well
plt.xlim(0, max(max(sorted_avg_x_vals), 1))  # x-axis starts from 0
plt.ylim(0, max(max(sorted_avg_y_vals), 1.2))  # y-axis starts from 0

# Show the legend, grid, and plot
plt.legend()
plt.grid(True)
plt.show()