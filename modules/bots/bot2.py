import heapq as PriorityQueue;
from ..ship.utilities import get_open_neighbours;
from ..constants import *;
import math;
import numpy as np;
import random;
import matplotlib.pyplot as plt;
import csv;
import time;

class Bot2:
    def __init__(self,maze,flammability):
        self.prev={};
        self.start=(None, None)
        self.end=(None, None)
        self.path=[];
        self.maze = maze
        self.flammability = flammability
        self.grid_size = maze.shape[0];
    
    def set_path(self):
        path=[];
        curr= tuple(self.end);
        while curr is not None:
            path.append((curr));
            curr=self.prev[tuple(curr)];
        path.reverse();
        self.path=path;

    def move_and_get_position(self):
        return self.path.pop(0)
    
    def execute_strategy(self,maze,start,end):
        print(f"start and end : {start},{end}")
        fringe=[(0,start)];
        self.start=start
        self.end=end
        PriorityQueue.heapify(fringe);
        totalCosts={start:0}
        prev={start:None}
        while bool(fringe):
            # print(f"in while {fringe}")
            curr=PriorityQueue.heappop(fringe)[1]
            if curr == end:
                self.prev=prev
                return True,prev,totalCosts;
            # print(f"Fringe->{curr}:{fringe}")
            # print(f"Neighbours of curr {curr}->{get_open_neighbours(maze,curr[0],curr[1])[1]}")
            for child in get_open_neighbours(maze,curr[0],curr[1])[1]:
                # print(f"processing child: {child}")
                cost = totalCosts[tuple(curr)] + 1;
                if tuple(child) not in totalCosts:
                    prev[tuple(child)]=curr;
                    totalCosts[tuple(child)]=cost;
                    # print(f"Adding {child} to the fringe")
                    PriorityQueue.heappush(fringe,(cost,child));
                if cost < totalCosts[tuple(child)] :
                    prev[tuple(child)]=curr;
                    totalCosts[tuple(child)]=cost;
                    #replace item in fringe
                    print(f"Updating {child} to the fringe")
                    # fringe= list(filter(lambda x: x[1]!=child[1],fringe))
                    fringe= list(filter(lambda x: not np.array_equal(x[1], child),fringe))
                    PriorityQueue.heappush(fringe,(cost,child));
        self.prev=prev;
        print('failed')
        return False,prev,totalCosts;

    def run_simulation(self,num_time_steps=math.inf,show_animation=True):
        t=0;
        ## At time t = 0, place the bot, the button, and the initial fire cell at random and distinct open cells in the ship
        open_cells=np.argwhere(self.maze==OPENED);
        random.seed(time.time_ns()+100^2);  
        random_cells=random.sample(list(open_cells),3);
        initial_values=[START,BUTTON,FIRE]
        for (x,y) in random_cells:
            self.maze[x][y]=initial_values.pop();
        (x_start,y_start)=np.argwhere(self.maze == START)[0]
        (x_button,y_button)=np.argwhere(self.maze == BUTTON)[0]
        print(f"Initial Fire cell -> {np.argwhere(self.maze == FIRE)[0]}")
        status=self.execute_strategy(self.maze,(x_start,y_start),(x_button,y_button))[0];
        if(not status):
            print(f"No short path found :(");
            plt.close();
            return;
        else:
            print("path found")
            self.set_path();
        simulation_status=False;
        while t < num_time_steps:
            print(f"At timestep t={t}");
            (x,y)=self.move_and_get_position();
            print(f"curr postion -> {(x,y)}")
            if (x,y) == (x_button,y_button): # Check if Bot has reached the button
                print("Bot reached the Button.SUCCESS!")
                simulation_status=True;
                break;
            if np.any(np.all(np.argwhere(self.maze == FIRE) == [x, y], axis=1))==True: # To check if bot reached the FIRE.
                print(f"Bot and Fire are in the same cell {(x,y)}. Failure.")
                # print(f"Fire Cells -> {np.argwhere(self.maze == FIRE)}")
                simulation_status=False;
                break;
            if ((x_start,y_start)!=(x,y)) : self.maze[x][y]=PATH
            self.spread_fire();
            yield self.get_maze_with_fire_blocks(); #Enable this line to see visualization.
            if np.any(np.all(np.argwhere(self.maze == FIRE) == [x_button,y_button], axis=1))==True: # To check if fire reached the Button.
                print("Fire reached the Button. Failure.")
                simulation_status=False;
                break;
            if (self.fire_in_path()== True):
                print("Bot 2 recalculating the path");
                status=self.execute_strategy(self.maze,(x,y),(x_button,y_button))[0];
                if(not status):
                    print(f"No short path found after recalculating.")
                    simulation_status=False;
                    break;
                self.set_path();self.move_and_get_position();
            t=t+1
        data=[int(simulation_status),self.flammability,self.grid_size,'bot2'];
        # Enable the below snippet for Data generation
        # plt.close();
        # with open('gd_bot2.csv',mode='a',newline='') as file:
        #     writer=csv.writer(file);
        #     writer.writerow(data);
        ###########
        return data;

    def spread_fire(self):
        open_cells=np.argwhere(
                        (self.maze == OPENED) | 
                        (self.maze == PATH) | 
                        (self.maze == BUTTON) | 
                        (self.maze == START)
                    );
        q=self.flammability;
        print(f"Fire Spread: No of cells fired so far: {np.argwhere(self.maze == FIRE).shape[0]}")
        fire_cells_dict=dict();
        for curr_cell in open_cells:
            x=int(curr_cell[0]);y=int(curr_cell[1]);
            # print(f"At cell {x,y}")
            k=self.get_fire_neighbours(x,y)[0];
            fire_cells_dict[(x,y)]=k;
        for curr_cell in open_cells:
            x=int(curr_cell[0]);y=int(curr_cell[1]);
            k=fire_cells_dict[(x,y)] 
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

    def fire_in_path(self):
        print(f"Checking if there is fire in the path. Curr -> {self.path[0]}")
        for cell in self.path:
            [x,y]=cell;
            if np.any(np.all(np.argwhere(self.maze == FIRE) == [x, y], axis=1))==True:
                print(f"Found Fire in the path at {[x,y]}")
                return True 
        return False;