import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# Initialize a dictionary to store winnability values for each q
winnability_results = defaultdict(list)

# Read the CSV file and collect winnability values for each q
with open('winnability.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        winnability = int(row[0])  # Winnability is the 0th index (either 0 or 1)
        q = float(row[1])  # q is the 1st index (convert to float)
        
        # Append the winnability to the list corresponding to the q value
        winnability_results[q].append(winnability)

# Calculate average winnability for each q value
average_winnability = []
q_values = sorted(winnability_results.keys())  # Sort q values

for q in q_values:
    avg_winnability = np.mean(winnability_results[q])  # Averaging the winnability for each q
    average_winnability.append(avg_winnability)

# Plotting the graph
plt.plot(q_values, average_winnability, marker='o', linestyle='-', color='b', label='Winnability')
plt.xlabel('q (Flammability)')
plt.ylabel('Winnability')
plt.title('Winnability vs. Flammability (q)')
plt.grid(True)
plt.legend()
plt.show()