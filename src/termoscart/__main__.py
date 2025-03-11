import argparse
import time
from multiprocessing import Pipe

import termoscart as toa


class Termoscart:
    def __init__(self, args: argparse.Namespace, F: toa.f.F) -> None:
        self.args = args
        self.F = F(args)
        self.plt = toa.CliPlot(args.rect_ratio, args.fgc, args.bgc, args.s)
        self.p1, self.p2 = Pipe()

    def loop(self) -> None:
        self.plt.animate(self.p1)
        N, T, F, p = self.args.N, self.args.T, self.F, self.p2
        w = -N
        while True:
            c_time = time.time_ns()
            p.send(F(w/N))
            if w == N-1:
                w = -N
            else:
                w += 1
            while time.time_ns() <= c_time + (T/2/N*1e9):
                time.sleep(1e-6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-T", "--period", dest="T", type=float, default=1, help="T=1/f, the time, until the figure has finished 1 cycle.")
    parser.add_argument("-N", "--resolution", dest="N", type=int, default=100, help="The delta between two points.")
    parser.add_argument("-r", "--rect-ratio", type=float, default=1/2, help="Width/Height")
    parser.add_argument("-s", "--symbol", dest="s", type=str, default=".", help="Symbol")
    parser.add_argument("-f", "--foreground-color", dest="fgc", type=str, default=None, help="Foreground color.")
    parser.add_argument("-b", "--background-color", dest="bgc", type=str, default=None, help="Background color.")
    subparser = parser.add_subparsers(dest="curve")

    F = toa.F(subparser)
    args = parser.parse_args()

    termoscart = Termoscart(args, F)

    try:
        termoscart.loop()
    except KeyboardInterrupt:
        termoscart.plt.proc.kill()
        time.sleep(1)
        termoscart.plt._colorize()


if __name__ == "__main__":
    main()
