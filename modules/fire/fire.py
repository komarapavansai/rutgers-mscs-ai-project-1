import math;
import numpy as np;
import random;
from ..constants import *;

class Fire:
    def __init__(self,maze,flammability):
        self.maze = maze
        self.flammability = flammability
        self.grid_size = maze.shape[0];
    
    def run_simulation(self,num_time_steps=math.inf):
        t=0;
        while t < num_time_steps:
            print(f"At timestep t={t}");
            self.spread_fire();
            yield self.get_maze_with_fire_blocks();
            t=t+1


    def spread_fire(self):
        open_cells=np.argwhere(self.maze == OPENED);
        q=self.flammability;
        print(f"Fire Spread: No of cells fired so far: {np.argwhere(self.maze == FIRE).shape[0]}")
        for curr_cell in open_cells:
            x=int(curr_cell[0]);y=int(curr_cell[1]);
            # print(f"At cell {x,y}")
            k=self.get_fire_neighbours(x,y)[0];
            fire_spread_probability= 1 - (1-q)**k
            # print(f"p-> {fire_spread_probability}, k-> {k}")
            if ( random.random() < fire_spread_probability ):
                self.maze[x,y]= FIRE # set cell on Fire !
                print(f"The cell({x},{y} is set on FIRE with propability p={fire_spread_probability})");
            else:
                print(f"The cell({x},{y} didnt set on FIRE with propability p={fire_spread_probability})")

    def get_maze_with_fire_blocks(self):
        print(f"No of cells fired so far: {np.argwhere(self.maze == FIRE).shape[0]}")
        return self.maze;

    def get_fire_neighbours(self,row,col):
        count=0;
        neighbours=[]

        if ( col-1 >=0 and self.maze[row][col-1]==FIRE) :
            count=count+1;neighbours.append([row,col-1])
        if (col+1 < self.grid_size and self.maze[row][col+1]==FIRE) :
            count=count+1;neighbours.append([row,col+1])
        if (row-1 >=0 and self.maze[row-1][col]==FIRE) :
            count=count+1;neighbours.append([row-1,col])
        if (row+1 < self.grid_size and self.maze[row+1][col]==FIRE) :
            count=count+1;neighbours.append([row+1,col])
        return (count,neighbours);