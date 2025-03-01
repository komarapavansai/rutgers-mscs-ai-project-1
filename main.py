from modules.ship.ship import Ship;
from modules.ship.visualizer import generate_grid,animation_function;
from modules.constants import *;
from modules.fire.fire import Fire;
from modules.bots.bot1 import Bot1;
from modules.bots.bot2 import Bot2;
import numpy as np;
import random;

def main():
    # ship = Ship(input('Enter the grid size of the Ship: '));
    # ship.desigShipLayout();
    # print(ship.maze)
    # bot= Bot2(maze=ship.maze,flammability=0.5);
    # animation_function(bot.run_simulation());

    #Generate data for Bot1
    for i in range(int(0 * 100), int(1 * 100) + 1, int(0.01 * 100)):
        q=(i / 100);
        for itr in range(0,20):
            ship = Ship(random.randint(15,60));
            print(f"Starting the simulation for bot1 for q:{q}, ship_size:{ship.grid_size} and iteration:{itr+1}")
            ship.desigShipLayout();
            bot= Bot1(maze=ship.maze,flammability=q);
            bot.run_simulation();

    #Generate data for Bot2
    for i in range(int(0 * 100), int(1 * 100) + 1, int(0.01 * 100)):
        q=(i / 100);
        for itr in range(0,20):
            ship = Ship(random.randint(25,60));
            print(f"Starting the simulation for bot2 for q:{q}, ship_size:{ship.grid_size}  and iteration:{itr+1}");
            ship.desigShipLayout();
            bot= Bot2(maze=ship.maze,flammability=q);
            animation_function(bot.run_simulation());

    # generate_grid(grid=fire.get_maze_with_fire_blocks());

if __name__ == "__main__":
    main()