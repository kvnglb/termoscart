import argparse
import time
from multiprocessing import Pipe, Process

from .cliplot import CliPlot
from .f import F


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-P", "--period", metavar="<seconds>", type=float, default=3, help="time in seconds, until the figure finishes 1 cycle (f=1/T) (default: %(default)s)")
    parser.add_argument("-R", "--resolution", metavar="<res>", type=int, default=100, help="delta between two points (default: %(default)s)")
    parser.add_argument("-r", "--rect-ratio", metavar="<width/height>", type=float, default=0.5, help="ratio of width/height (depending on the font, needed that a circle appears like a circle and not like an ellipse) (default: %(default)s)")
    parser.add_argument("-s", "--symbol", metavar="<char>", type=str, default="#", help="symbol for the curve (default: '%(default)s')")
    parser.add_argument("-l", "--line-color", metavar="<color>", type=str, default=None, help="color of the curve (default: %(default)s)")
    parser.add_argument("-b", "--background-color", metavar="<color>", type=str, default=None, help="color of the background (default: %(default)s)")
    parser.add_argument("-g", "--grid", action="store_true", help="enables grid (default: %(default)s)")
    parser.add_argument("-G", "--grid-color", metavar="<color>", type=str, help="color of the grid (default: %(default)s)")
    subparser = parser.add_subparsers(dest="curve")

    func = F(subparser)
    args = parser.parse_args()

    plt = CliPlot(args)

    p1, p2 = Pipe(False)
    if args.grid or args.grid_color:
        p = plt.animate_with_grid
    else:
        p = plt.animate
    proc = Process(target=p, args=(p1,), daemon=True)
    proc.start()

    try:
        P, R, f = args.period, args.resolution, func(args)
        w = -R
        while True:
            c_time = time.time_ns()
            p2.send(f(w/R))
            if w == R-1:
                w = -R
            else:
                w += 1
            while time.time_ns() <= c_time + (P/2/R*1e9):
                time.sleep(1e-6)

    except KeyboardInterrupt:
        proc.kill()
        while proc.is_alive():
            time.sleep(0.1)
        plt.colorize(reset=True)
        plt.paint_screen()


if __name__ == "__main__":
    main()
