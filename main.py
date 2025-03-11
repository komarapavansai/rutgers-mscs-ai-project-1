from modules.ship.ship import Ship;
from modules.ship.visualizer import generate_grid,animation_function;
from modules.constants import *;
from modules.fire.fire import Fire;
from modules.bots.bot1 import Bot1;
from modules.bots.bot2 import Bot2;
from modules.bots.bot3 import Bot3;
from modules.bots.bot4 import Bot4;
import numpy as np;
import random;

def main():
    ship = Ship(input('Enter the grid size of the Ship: '));
    ship.desigShipLayout();
    print(ship.maze)
    # bot= Bot4(maze=ship.maze,flammability=0.4,alpha=0.25);
    bot= Bot3(maze=ship.maze,flammability=0.4);
    animation_function(bot.run_simulation());

    #Generate data for Bot1
    # for itr in range(0,30):
    #     for i in range(int(0* 100), int(1 * 100) + 1, int(0.01 * 100)):
    #         q=(i / 100);
    #         ship = Ship(40);
    #         ship.desigShipLayout();
    #         maze1=ship.maze.copy();
    #         # print(np.argwhere(maze1==OPENED).__len__());
    #         print(f"Starting the simulation for bot1 for q:{q}, ship_size:{ship.grid_size} and iteration:{itr+1}");
    #         bot=Bot1(maze=maze1,flammability=q);
    #         bot.run_simulation();

    #Generate data for Bot2
    # for itr in range(0,30):
    #     for i in range(int(0* 100), int(1 * 100) + 1, int(0.01 * 100)):
    #         q=(i / 100);
    #         ship = Ship(40);
    #         ship.desigShipLayout();
    #         maze1=ship.maze.copy();
    #         print(np.argwhere(maze1==OPENED).__len__());
    #         print(f"Starting the simulation for bot2 for q:{q}, ship_size:{ship.grid_size} and iteration:{itr+1}");
    #         bot=Bot2(maze=maze1,flammability=q);
    #         bot.run_simulation();

    #Generate data for Bot3
    # for i in range(int(0* 100), int(1 * 100) + 1, int(0.01 * 100)):
    #     q=(i / 100);
    #     ship = Ship(40);
    #     ship.desigShipLayout();
    #     for itr in range(0,30):
    #         maze1=ship.maze.copy();
    #         print(f"Starting the simulation for bot4 for q:{q}, ship_size:{ship.grid_size} and iteration:{itr+1}");
    #         bot=Bot3(maze=maze1,flammability=q);
    #         bot.run_simulation();

    #Generate data for Bot4
    # for i in range(int(0.36* 100), int(1 * 100) + 1, int(0.01 * 100)):
    #     q=(i / 100);
    #     ship = Ship(40);
    #     ship.desigShipLayout();
    #     for itr in range(0,30):
    #         maze1=ship.maze.copy();
    #         print(f"Starting the simulation for bot4 for q:{q}, ship_size:{ship.grid_size} and iteration:{itr+1}");
    #         bot=Bot4(maze=maze1,flammability=q,alpha=0.25);
    #         bot.run_simulation();

    # generate_grid(grid=fire.get_maze_with_fire_blocks());

if __name__ == "__main__":
    main()