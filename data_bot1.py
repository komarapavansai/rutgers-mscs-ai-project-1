import numpy as np
import pandas as pd;
from modules.ship.ship import Ship;
from modules.ship.visualizer import generate_grid,animation_function;
from modules.constants import *;
from modules.fire.fire import Fire;
from modules.bots.bot1 import Bot1;
from modules.bots.bot2 import Bot2;
from modules.bots.bot3 import Bot3;
from modules.bots.bot4 import Bot4;
import random;

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

# # Print the shape of the resulting 3D array
# print("Shape of the 3D array:", ship_arrays[0].shape)

# print(np.argwhere(ship_arrays[0] == 2))


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

#Generate data for Bot1
for itr in range(0,30):
    for i in range(int(0.97* 100), int(1 * 100) + 1, int(0.01 * 100)):
        q=(i / 100);
        maze1=ship_arrays[random.randint(0,14999)].copy();
        [x,y] = np.argwhere(maze1 == 2)[0];
        maze1[x][y]=0;
        [x,y] = np.argwhere(maze1 == 3)[0];
        maze1[x][y]=0;
        [x,y] = np.argwhere(maze1 == 4)[0];
        maze1[x][y]=0;
        open_cells=np.argwhere(maze1==OPENED);
        # random_cells=random.sample(list(open_cells),3);
        random_cells=[(0,0),(10,15),(10,16)];
        initial_values=[START,BUTTON,FIRE]
        for (x,y) in random_cells:
            maze1[x][y]=OPENED;
            maze1[x][y]=initial_values.pop();
        # print(f"Starting the simulation for bot1 for q:{q}, ship_size:{maze1.shape[0]} and iteration:{itr+1}");
        # bot1=Bot1(maze=maze1.copy(),flammability=q);
        # bot1.run_simulation();
        # print(f"Starting the simulation for bot2 for q:{q}, ship_size:{maze1.shape[0]} and iteration:{itr+1}");
        # bot2=Bot2(maze=maze1.copy(),flammability=q);
        # bot2.run_simulation();
        # print(f"Starting the simulation for bot3 for q:{q}, ship_size:{maze1.shape[0]} and iteration:{itr+1}");
        # bot3=Bot3(maze=maze1.copy(),flammability=q);
        # bot3.run_simulation();
        print(f"Starting the simulation for bot4 for q:{q}, ship_size:{maze1.shape[0]} and iteration:{itr+1}");
        bot4=Bot4(maze=maze1.copy(),flammability=q);
        bot4.run_simulation();