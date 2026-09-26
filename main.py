"""Launch the visual comparison or export it as an animated GIF."""
import argparse


def main():
    parser = argparse.ArgumentParser(description='This Bot Is on Fire | AI strategy lab')
    parser.add_argument('--size', type=int, default=25, help='Grid dimension, 5 to 80; assignment target: 40')
    parser.add_argument('--q', type=float, default=0.22, help='Flammability, 0 to 1')
    parser.add_argument('--seed', type=int, default=23, help='Reproducible scenario seed')
    parser.add_argument('--export', metavar='FILE.gif', help='Export a GIF without opening a window')
    parser.add_argument('--max-steps', type=int, default=180, help='Maximum exported turns')
    args = parser.parse_args()
    from modules.simulation import Simulation
    try:
        sim = Simulation(args.size, args.q, args.seed)
        if args.max_steps < 1:
            raise ValueError('max-steps must be positive.')
        if args.export and not args.export.lower().endswith('.gif'):
            raise ValueError('Export filename must end in .gif.')
    except ValueError as exc:
        parser.error(str(exc))
    from modules.dashboard import Dashboard
    dashboard = Dashboard(sim)
    if args.export:
        dashboard.export(args.export, args.max_steps)
    else:
        dashboard.run()


if __name__ == '__main__':
    main()
