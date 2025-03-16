import argparse
import time
from multiprocessing import Pipe, Process

from .cliplot import CliPlot, COLOR
from .f import F


def settings() -> None:
    print()
    print("width/height")
    print("============")
    print()
    print("To display a square not like an rectangle (or a circle not like an ellipse),")
    print("count the pixels from")
    print("  - the first column to the last column. This is the width.")
    print("  - the first row the the last row. This is the height.")
    print("Calculate width/height. This is the value to use for '--rect-ratio'")
    print("to show the animation with proper proportions.")
    for _ in range(11):
        print("." * 10)

    print()
    print()
    print("colors")
    print("======")
    print()
    print("{:<15} | {:<5}".format("line-color", "background-color"))
    print("-" * 29)
    for key, color in COLOR.items():
        if key:
            print("\033[{}m{:<15}\033[0m | \033[{}m{}\033[0m".format(color, key, color+10, key))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", action="store_true", help="shows information about the rect-ratio and colors (default: %(default)s)")
    parser.add_argument("-P", "--period", metavar="<seconds>", type=float, default=3, help="time in seconds, until the figure finishes 1 cycle (f=1/T) (default: %(default)s)")
    parser.add_argument("-R", "--resolution", metavar="<res>", type=int, default=100, help="delta between two points (default: %(default)s)")
    parser.add_argument("-r", "--rect-ratio", metavar="<width/height>", type=float, default=0.5, help="ratio of width/height (depending on the font, needed that a circle appears like a circle and not like an ellipse) (default: %(default)s)")
    parser.add_argument("-s", "--symbol", metavar="<char>", type=str, default="#", help="symbol for the curve (default: '%(default)s')")
    parser.add_argument("-l", "--line-color", metavar="<color>", type=str, default=None, help="color of the curve (default: %(default)s)")
    parser.add_argument("-b", "--background-color", metavar="<color>", type=str, default=None, help="color of the background (default: %(default)s)")
    parser.add_argument("-g", "--grid", action="store_true", help="enables grid (default: %(default)s)")
    parser.add_argument("-G", "--grid-color", metavar="<color>", type=str, help="color of the grid (default: %(default)s)")
    parser.add_argument("-f", "--frame", metavar="<frame>", type=float, help="shows the curve at a certain frame without animation, value must be between -1 and 1 (default: %(default)s)")
    subparser = parser.add_subparsers(dest="curve")

    func = F(subparser)
    args = parser.parse_args()

    if args.settings:
        settings()
        return

    plt = CliPlot(args)
    f = func(args)

    if args.frame is not None:
        if args.grid or args.grid_color:
            plt.draw_grid()
        plt.scatter(*f(args.frame))
        plt.show()
        plt.colorize(reset=True)
        return

    p1, p2 = Pipe(False)
    if args.grid or args.grid_color:
        p = plt.animate_with_grid
    else:
        p = plt.animate
    proc = Process(target=p, args=(p1,), daemon=True)
    proc.start()

    try:
        P, R = args.period, args.resolution
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
