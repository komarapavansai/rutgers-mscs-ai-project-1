from modules.ship.ship import Ship;

def main():
    ship = Ship(input('Enter the grid size of the Ship: '));
    ship.desigShipLayout();
    print(ship.maze)

if __name__ == "__main__":
    main()