import argparse
import time
from multiprocessing import Pipe, Process

import termoscart as toa


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-T", "--period", dest="T", type=float, default=3, help="T=1/f, the time, until the figure has finished 1 cycle.")
    parser.add_argument("-N", "--resolution", dest="N", type=int, default=100, help="The delta between two points.")
    parser.add_argument("-r", "--rect-ratio", type=float, default=1/2, help="Width/Height")
    parser.add_argument("-s", "--symbol", dest="s", type=str, default=".", help="Symbol")
    parser.add_argument("-f", "--foreground-color", dest="fgc", type=str, default=None, help="Foreground color.")
    parser.add_argument("-b", "--background-color", dest="bgc", type=str, default=None, help="Background color.")
    subparser = parser.add_subparsers(dest="curve")

    F = toa.F(subparser)
    args = parser.parse_args()

    plt = toa.CliPlot(args)

    p1, p2 = Pipe(False)
    proc = Process(target=plt.animate, args=(p1,), daemon=True)
    proc.start()

    try:
        N, T, f = args.N, args.T, F(args)
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
        plt._colorize()
        plt.paint_screen()


if __name__ == "__main__":
    main()
