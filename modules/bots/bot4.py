import heapq as PriorityQueue;
from ..ship.utilities import get_open_neighbours;
from ..constants import *;
import math;
import numpy as np;
import random;
import matplotlib.pyplot as plt;
import csv;
import time;

class Bot4:
    def __init__(self,maze,flammability,alpha=0.5):
        self.prev={};
        self.start=(None, None)
        self.end=(None, None)
        self.visits={};
        self.actions={};
        self.risk={};
        self.path=[];
        self.maze = maze;
        self.flammability = flammability;
        self.alpha= alpha;
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
            self.visits[curr] = self.visits.get(curr,0) + 1;
            # print(f"Fringe->{curr}:{fringe}")
            # print(f"Neighbours of curr {curr}->{get_open_neighbours(maze,curr[0],curr[1])[1]}")
            for child in get_open_neighbours(maze,curr[0],curr[1])[1]:
                # print(f"processing child: {child}")
                '''The goal here is to calculate f(x) = g(x) + h(x), here x=child
                f(x)=total_risk,g(x)=risk_till_child, h(x)=remaining_risk 
                '''
                self.actions[(curr,child)]=self.actions.get((curr,child),0) +1;
                self.risk[(curr,child)]=self.risk.get((curr,child),0) + self.calcuate_risk(child[0],child[1]);

                cost = totalCosts[tuple(curr)] + self.calcuate_risk(child[0],child[1]);  # Calculating g(child)
                total_risk= cost + self.ucb_of_risk(curr,child); # Calculating f(x) for A* estimation
                if tuple(child) not in totalCosts:
                    prev[tuple(child)]=curr;
                    totalCosts[tuple(child)]=cost;
                    # print(f"Adding {child} to the fringe")
                    PriorityQueue.heappush(fringe,(total_risk,child));
                if cost < totalCosts[tuple(child)] :
                    prev[tuple(child)]=curr;
                    totalCosts[tuple(child)]=cost;
                    #replace item in fringe
                    # print(f"Updating {child} to the fringe")
                    # print(f"the fringe-> {fringe}")
                    fringe= list(filter(lambda x: not np.array_equal(x[1], child),fringe))
                    PriorityQueue.heappush(fringe,(total_risk,child));
        self.prev=prev;
        print('failed')
        return False,prev,totalCosts;

    def calcuate_risk(self,x,y):
        distance_of_fire_from_cell=self.get_nearest_fire_distance(x,y);
        distance_of_goal_from_cell=abs(x-self.end[0])+abs(y-self.end[1]);
        risk=distance_of_goal_from_cell - self.alpha*distance_of_fire_from_cell;
        if risk < 0:
            return float('inf');
        return risk;
    
    def get_nearest_fire_distance(self,x,y):
        fire_cells=np.argwhere(self.maze==FIRE);
        min_distance=float('inf');
        for each_cell in fire_cells:
            min_distance = min(min_distance,abs(x-each_cell[0])+abs(y-each_cell[1]));
        if min_distance == float('inf'):
            return 0;
        return min_distance;
    
    # def fire_spread_probability(self,x,y):
    #     k=self.get_fire_neighbours(x,y)[0];
    #     fire_spread_probability= 1 - (1-self.flammability)**k
    #     return fire_spread_probability;

    def ucb_of_risk(self,curr,child):
        
        risk_from_curr_to_child=self.risk[(curr,child)];
        count_from_curr_to_child=self.actions[(curr,child)];
        curr_visited_count = self.visits[curr];

        # print(f"curr->{curr};child->{child};risk-> {risk_from_curr_to_child};count_from_curr_to_child-> {count_from_curr_to_child}; curr_visited_count -> {curr_visited_count}");
    
        return (risk_from_curr_to_child/count_from_curr_to_child)\
            + math.sqrt((2* math.log(curr_visited_count))/count_from_curr_to_child);
    

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
            # yield self.get_maze_with_fire_blocks();
            if np.any(np.all(np.argwhere(self.maze == FIRE) == [x_button,y_button], axis=1))==True: # To check if fire reached the Button.
                print("Fire reached the Button. Failure.")
                simulation_status=False;
                break;
            status=self.execute_strategy(self.maze,(x,y),(x_button,y_button))[0];
            if(not status):
                print(f"No short path found after recalculating.")
                simulation_status=False;
                break;
            self.set_path();self.move_and_get_position();
            t=t+1
        plt.close();
        data=[int(simulation_status),self.flammability,self.grid_size,'bot4',self.alpha];
        with open('graph_data_bot4.csv',mode='a',newline='') as file:
            writer=csv.writer(file);
            writer.writerow(data);

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
