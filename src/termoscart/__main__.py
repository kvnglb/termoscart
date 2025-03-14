import argparse
import time
from multiprocessing import Pipe, Process

from .cliplot import CliPlot
from .f import F


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-T", "--period", dest="T", type=float, default=3, help="T=1/f, the time, until the figure has finished 1 cycle.")
    parser.add_argument("-N", "--resolution", dest="N", type=int, default=100, help="The delta between two points.")
    parser.add_argument("-r", "--rect-ratio", type=float, default=1/2, help="Width/Height")
    parser.add_argument("-s", "--symbol", dest="s", type=str, default=".", help="Symbol")
    parser.add_argument("-f", "--foreground-color", dest="fgc", type=str, default=None, help="Foreground color.")
    parser.add_argument("-b", "--background-color", dest="bgc", type=str, default=None, help="Background color.")
    parser.add_argument("-g", "--grid", action="store_true", help="Enable grid")
    parser.add_argument("-c", "--grid-color", dest="gc", type=str, help="Color of the grid")
    subparser = parser.add_subparsers(dest="curve")

    func = F(subparser)
    args = parser.parse_args()

    plt = CliPlot(args)

    p1, p2 = Pipe(False)
    if args.grid:
        p = plt.animate_with_grid
    else:
        p = plt.animate
    proc = Process(target=p, args=(p1,), daemon=True)
    proc.start()

    try:
        N, T, f = args.N, args.T, func(args)
        w = -N
        while True:
            c_time = time.time_ns()
            p2.send(f(w/N))
            if w == N-1:
                w = -N
            else:
                w += 1
            while time.time_ns() <= c_time + (T/2/N*1e9):
                time.sleep(1e-6)

    except KeyboardInterrupt:
        proc.kill()
        while proc.is_alive():
            time.sleep(0.1)
        plt.colorize(reset=True)
        plt.paint_screen()


if __name__ == "__main__":
    main()
