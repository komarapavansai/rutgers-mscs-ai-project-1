from modules.ship.ship import Ship;
from modules.ship.visualizer import generate_grid,animation_function;
from modules.constants import *;
from modules.fire.fire import Fire;
from modules.bots.bot1 import Bot1;
import numpy as np;

def main():
    ship = Ship(input('Enter the grid size of the Ship: '));
    ship.desigShipLayout();
    print(ship.maze)
    # generate_grid(ship.maze);

    fire = Fire(maze=ship.maze,flammability=0.4);
    bot1= Bot1();
    animation_function(fire.run_simulation(bot=bot1));
    # generate_grid(grid=fire.get_maze_with_fire_blocks());

if __name__ == "__main__":
    main()