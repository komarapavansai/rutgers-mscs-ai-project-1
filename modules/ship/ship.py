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
        maze[random.randint(0,self.grid_size-1)][random.randint(0,self.grid_size-1)]= FIRE # -1 indicates an Open cell.
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

    def getBlockedCells(self, arr):
         return np.argwhere(arr==BLOCKED)

    def ifExpansionPossbile(self):
        # SCOPE FOR IMPROVEMENT THE CODE COMPLEXITY
        for i in range(0,self.grid_size):
            for j in range(0, self.grid_size):
                if self.maze[i][j]==BLOCKED and self.getOpenNeighboursCount(i,j)[0]==1:
                    return True;
        return False;
    
    def desigShipLayout(self):
        while ( self.ifExpansionPossbile()):
            blockedCells = self.getBlockedCells(self.maze);
            random_cell = blockedCells[np.random.choice(blockedCells.shape[0])];
            neighbourCount,neighbours= self.getOpenNeighboursCount(random_cell[0],random_cell[1])
            if neighbourCount == 1:
                self.maze[random_cell[0]][random_cell[1]]=OPENED;
