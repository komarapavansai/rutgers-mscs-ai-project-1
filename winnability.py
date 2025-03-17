import numpy as np
import pandas as pd;
from modules.ship.ship import Ship;
from modules.constants import *;
from modules.bots.bot1 import Bot1;
from modules.bots.bot2 import Bot2;
from modules.bots.bot3 import Bot3;
from modules.bots.bot4 import Bot4;
import random;
import csv;

# Function to convert string representation of matrix into numpy array
def str_to_array(matrix_str):
    # Remove any unwanted characters such as extra brackets or commas
    matrix_str = matrix_str.strip().replace('[', '').replace(']', '')  # Remove brackets
    rows = matrix_str.split(',')  # Split by commas instead of new lines
    matrix = np.array([list(map(int, row.split())) for row in rows if row])  # Convert to 2D numpy array
    return matrix

# Read the CSV file using pandas
df = pd.read_csv('shipgeneration.csv')

# List to store the numpy arrays
ship_arrays = []

# Iterate over the 6th column (index 5) and convert each matrix string to a numpy array
for matrix_str in df.iloc[:, 5]:  # Get all data in the 6th column
    if isinstance(matrix_str, str) and matrix_str.strip():  # Check if it's a non-empty string
        try:
            matrix = str_to_array(matrix_str)  # Convert to numpy array
            ship_arrays.append(matrix)  # Add to the list
        except Exception as e:
            print(f"Error processing matrix: {e}")

# Convert the list of numpy arrays to a 3D numpy array
ship_arrays_3d = np.array(ship_arrays)
ship_arrays = ship_arrays_3d.reshape(-1, 40, 40)

print('Data Processed');
# maze1=ship_arrays[random.randint(0,14999)].copy();
# print(f"{np.argwhere(maze1== 2)}")
# print(f"{np.argwhere(maze1 == 3)}")
# print(f"{np.argwhere(maze1 == 4)}")
# [x,y] = np.argwhere(maze1 == 2)[0];
# maze1[x][y]=OPENED;
# [x,y] = np.argwhere(maze1 == 3)[0];
# maze1[x][y]=OPENED;
# [x,y] = np.argwhere(maze1 == 4)[0];
# maze1[x][y]=OPENED;
# print(f"The percent of open cells: {(len(np.argwhere(maze1 == OPENED))/(maze1.shape[0]*maze1.shape[0]))*100}%")
# print(f"{np.argwhere(maze1 > 1)}")
# bot= Bot1(maze=maze1,flammability=0.4);
# animation_function(bot.run_simulation());

for itr in range(0,100):
    for i in range(int(1* 100), int(1 * 100) + 1, int(0.01 * 100)):
        q=(i / 100);
        maze1=ship_arrays[random.randint(0,14999)].copy();
        [x,y] = np.argwhere(maze1 == 2)[0];
        maze1[x][y]=0;
        [x,y] = np.argwhere(maze1 == 3)[0];
        maze1[x][y]=0;
        [x,y] = np.argwhere(maze1 == 4)[0];
        maze1[x][y]=0;
        open_cells=np.argwhere(maze1==OPENED);
        random_cells=random.sample(list(open_cells),3);
        initial_values=[START,BUTTON,FIRE]
        for (x,y) in random_cells:
            maze1[x][y]=initial_values.pop(0);
        winnability=0;
        successful_bots=[];
        print(f"Starting the simulation for bot4 for q:{q}, ship_size:{maze1.shape[0]} and iteration:{itr+1}")

        # Run bot4 simulation
        bot4 = Bot4(maze=maze1.copy(), flammability=q)
        bot4_status = bot4.run_simulation()
        if bot4_status is None:
            bot4_status = [0]

        if bot4_status[0] == 1:
            winnability = 1
            successful_bots.append('bot4')
        else:
            # If bot4 fails, run bot3
            print(f"Bot3 failed. Starting the simulation for bot2 for q:{q}, ship_size:{maze1.shape[0]} and iteration:{itr+1}")
            bot3 = Bot3(maze=maze1.copy(), flammability=q)
            bot3_status = bot3.run_simulation()
            if bot3_status is None:
                bot3_status = [0]

            if bot3_status[0] == 1:
                winnability = 1
                successful_bots.append('bot3')
            else:
                # If bot3 fails, run bot2
                print(f"Bot2 failed. Starting the simulation for bot4 for q:{q}, ship_size:{maze1.shape[0]} and iteration:{itr+1}")
                bot2 = Bot2(maze=maze1.copy(), flammability=q)
                bot2_status = bot2.run_simulation()
                if bot2_status is None:
                    bot2_status = [0]

                if bot2_status[0] == 1:
                    winnability = 1
                    successful_bots.append('bot2')
                else:
                    # If bot2 fails, run bot1
                    print(f"Bot4 failed. Starting the simulation for bot1 for q:{q}, ship_size:{maze1.shape[0]} and iteration:{itr+1}")
                    bot1 = Bot1(maze=maze1.copy(), flammability=q)
                    bot1_status = bot1.run_simulation()
                    if bot1_status is None:
                        bot1_status = [0]

                    if bot1_status[0] == 1:
                        winnability = 1
                        successful_bots.append('bot1');
                    else:
                        print(f"Bot1 failed.")

        # Write results to the CSV file
        data = [winnability, q, maze1.shape[0], successful_bots]
        with open('winnability.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
