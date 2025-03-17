import matplotlib.pyplot as plt
import csv
import numpy as np
from collections import defaultdict

# Define bot labels and colors
bot_labels = ['bot1', 'bot2', 'bot3', 'bot4']
# bot_labels = ['bot3']
colors = ['blue', 'green', 'red', 'purple']
# colors = ['red']
bot_files = [f'./gd_{i}.csv' for i in bot_labels]  # File paths for bot data

# Dictionary to store success rates grouped by flammability (q) for each bot
bot_data = {bot: defaultdict(list) for bot in bot_labels}

# Read CSV files and store data for "Average Frequency of Success"
for bot_label, file_name in zip(bot_labels, bot_files):
    with open(file_name, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 4 and row[3] == bot_label:  # Ensure correct bot data
                q = float(row[1])  # Flammability
                success = int(row[0])  # Winnability (0 or 1)
                bot_data[bot_label][q].append(success)

# Prepare data for "Winnability vs. Flammability (q)"
winnability_results = defaultdict(list)

# Read the winnability CSV
with open('winnability.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        winnability = int(row[0])  # Winnability (either 0 or 1)
        q = float(row[1])  # Flammability
        winnability_results[q].append(winnability)

# Calculate average winnability for each q value
q_values_win = sorted(winnability_results.keys())  # Sorted q values
average_winnability = [np.mean(winnability_results[q]) for q in q_values_win]  # Average success rate

# Plotting the graphs
plt.figure(figsize=(10, 6))  # Set figure size

# "Winnability vs. Flammability (q)" (Black solid line)
plt.plot(q_values_win, average_winnability, linestyle='-', color='black', label='Overall Winnability', linewidth=2)

# "Average Frequency of Success vs. Flammability (q)" for each bot
for i, bot_label in enumerate(bot_labels):
    x_vals = sorted(bot_data[bot_label].keys())  # Sorted q values
    y_vals = [sum(bot_data[bot_label][q]) / len(bot_data[bot_label][q]) for q in x_vals]  # Avg success rate

    # Plot as a connected line without markers
    plt.plot(x_vals, y_vals, linestyle='-', color=colors[i], label=bot_label, linewidth=2)

# Graph customization
plt.xlabel('q (Flammability)', fontsize=14)
plt.ylabel('Success Rate', fontsize=14)
plt.title('Success Rate of All bots & Winnability vs. Flammability', fontsize=16)
plt.legend()
plt.grid(True)
plt.xlim(0, 1)  # Flammability range [0,1]
plt.ylim(0, 1.2)  # Success rate range [0,1.2] for clarity

# Show plot
plt.show()
