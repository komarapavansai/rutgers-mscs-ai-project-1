import numpy as np;
import random;
from ..constants import *;

class Ship:

    def __init__(self,grid_size=5):
        self.grid_size=int(grid_size)
        # 0 indicates the blocked cells. Intilialize ship with all blocked cells.
        maze=np.full(fill_value=BLOCKED, dtype= int, shape=(self.grid_size,self.grid_size))
        # Set a random cell to Open Cell
        maze[random.randint(0,self.grid_size-1)][random.randint(0,self.grid_size-1)]= OPENED # 1 indicates an Open cell.
        self.maze= maze
        print(f"Initial grid :\n {self.maze}\n")

    def getOpenNeighboursCount(self,row,col):
        count=0;
        neighbours=[]

        if ( col-1 >=0 and self.maze[row][col-1]==OPENED) :
            count=count+1;neighbours.append([row,col-1])
        if (col+1 < self.grid_size and self.maze[row][col+1]==OPENED) :
            count=count+1;neighbours.append([row,col+1])
        if (row-1 >=0 and self.maze[row-1][col]==OPENED) :
            count=count+1;neighbours.append([row-1,col])
        if (row+1 < self.grid_size and self.maze[row+1][col]==OPENED) :
            count=count+1;neighbours.append([row+1,col])
        return (count,neighbours);

    def getBlockedNeighboursCount(self,row,col):
        count=0;
        neighbours=[]

        if ( col-1 >=0 and self.maze[row][col-1]==BLOCKED) :
            count=count+1;neighbours.append([row,col-1])
        if (col+1 < self.grid_size and self.maze[row][col+1]==BLOCKED) :
            count=count+1;neighbours.append([row,col+1])
        if (row-1 >=0 and self.maze[row-1][col]==BLOCKED) :
            count=count+1;neighbours.append([row-1,col])
        if (row+1 < self.grid_size and self.maze[row+1][col]==BLOCKED) :
            count=count+1;neighbours.append([row+1,col])
        return (count,neighbours);

    def getBlockedCells(self, arr):
         return np.argwhere(arr==BLOCKED)

    def ifExpansionPossbile(self):
        # SCOPE FOR IMPROVEMENT THE CODE COMPLEXITY
        # for i in range(0,self.grid_size):
        #     for j in range(0, self.grid_size):
        #         if self.maze[i][j]==BLOCKED and self.getOpenNeighboursCount(i,j)[0]==1:
        #             return True;
        # return False;
        blocked_cells=np.argwhere(self.maze == BLOCKED)
        for each_blocked_cell in blocked_cells:
            [x,y]=[each_blocked_cell[0],each_blocked_cell[1]];
            if self.getOpenNeighboursCount(x,y)[0]==1:
                return True;
        return False;

    def getDeadCells(self):
        deadCells=[];
        open_cells=np.argwhere(self.maze == OPENED)
        for each_open_cell in open_cells:
            [x,y]=[each_open_cell[0],each_open_cell[1]];
            if self.getOpenNeighboursCount(x,y)[0]==1:
                deadCells.append([x,y])
        return deadCells;

    def desigShipLayout(self):
        while ( self.ifExpansionPossbile()):
            blockedCells = self.getBlockedCells(self.maze);
            random_cell = blockedCells[np.random.choice(blockedCells.shape[0])];
            neighbourCount,neighbours= self.getOpenNeighboursCount(random_cell[0],random_cell[1])
            if neighbourCount == 1:
                self.maze[random_cell[0]][random_cell[1]]=OPENED;
        deadCells=self.getDeadCells();
        random.shuffle(deadCells);
        count=0;dead_cells_count=(len(deadCells)//2);
        while(count < dead_cells_count):
            eachCell=deadCells.pop();
            x=eachCell[0];y=eachCell[1];
            if self.getOpenNeighboursCount(x,y)[0]==1:
                _, closedNeighbours= self.getBlockedNeighboursCount(x,y);
                [row,col]=closedNeighbours[random.randint(0, len(closedNeighbours) - 1)];
                self.maze[row][col]=OPENED;
                count=count+1;
        print(f"The percent of open cells: {(len(np.argwhere(self.maze == OPENED))/(self.grid_size*self.grid_size))*100}%")
