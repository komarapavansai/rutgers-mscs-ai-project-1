import math;
import numpy as np;
import random;
from ..constants import *;

class Fire:
    def __init__(self,maze,flammability):
        self.maze = maze
        self.flammability = flammability
        self.grid_size = maze.shape[0];
    
    def run_simulation(self,bot,num_time_steps=math.inf):
        t=0;
        ## At time t = 0, place the bot, the button, and the initial fire cell at random and distinct open cells in the ship
        open_cells=np.argwhere(self.maze==OPENED);
        random_cells=random.sample(list(open_cells),3);
        initial_values=[START,BUTTON,FIRE]
        for (x,y) in random_cells:
            self.maze[x][y]=initial_values.pop();
        (x_start,y_start)=np.argwhere(self.maze == START)[0]
        (x_button,y_button)=np.argwhere(self.maze == BUTTON)[0]
        print(f"Initial Fire cell -> {np.argwhere(self.maze == FIRE)[0]}")
        status=bot.execute_strategy(self.maze,(x_start,y_start),(x_button,y_button))[0];
        bot.set_path();
        if(not status):
            print(f"No short path found :(")
            return;
        else:
            print("path found")
        while t < num_time_steps:
            print(f"At timestep t={t}");
            (x,y)=bot.move_and_get_position();
            # Add a condition check to see if bot is catching fire 
            # (x,y)=next(bot.move_and_get_position());
            print(f"curr postion -> {(x,y)}")
            if (x,y) == (x_button,y_button): # Check if Bot has reached the button
                print("Bot reached the Button.SUCCESS!")
                break;
            # if np.isin(np.argwhere(self.maze == FIRE), [x,y]).all(axis=1).any()==True: # To check if bot reached the FIRE.
            if np.any(np.all(np.argwhere(self.maze == FIRE) == [x, y], axis=1))==True: # To check if bot reached the FIRE.
                print(f"Bot and Fire are in the same cell {(x,y)}. Failure.")
                # print(f"Fire Cells -> {np.argwhere(self.maze == FIRE)}")
                break;
            if ((x_start,y_start)!=(x,y)) : self.maze[x][y]=PATH
            self.spread_fire();
            yield self.get_maze_with_fire_blocks();
            # if np.isin(np.argwhere(self.maze == FIRE), [x_button,y_button]).all(axis=1).any()==True: # To check if fire reached the Button.
            if np.any(np.all(np.argwhere(self.maze == FIRE) == [x_button,y_button], axis=1))==True: # To check if fire reached the Button.
                print("Fire reached the Button. Failure.")
                break;
            t=t+1


    def spread_fire(self):
        open_cells=np.argwhere(
                        (self.maze == OPENED) | 
                        (self.maze == PATH) | 
                        (self.maze == BUTTON) | 
                        (self.maze == START)
                    );
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
            # else:
                # print(f"The cell({x},{y} didnt set on FIRE with propability p={fire_spread_probability})")

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