import os
import sys
import typing as t
from argparse import Namespace
from multiprocessing.connection import Connection

COLORS = {None: 0,
          "black": 30,
          "red": 31,
          "green": 32,
          "yellow": 33,
          "blue": 34,
          "magenta": 35,
          "cyan": 36,
          "white": 37,
          "bright-black": 90,
          "bright-red": 91,
          "bright-green": 92,
          "bright-yellow": 93,
          "bright-blue": 94,
          "bright-magenta": 95,
          "bright-cyan": 96,
          "bright-white": 97}


class CliPlot:
    def __init__(self, args: Namespace) -> None:
        self.rect_ratio = args.rect_ratio
        self.s = args.s
        self.fgc = args.fgc
        self.bgc = args.bgc
        self.gc = args.gc

        size = os.get_terminal_size()
        self.columns = size.columns
        self.lines = size.lines - 1
        self.scale()
        self.clear_matrix()
        self.colorize()

    def colorize(self, reset: bool = False) -> None:
        if reset:
            sys.stdout.write("\033[0m")
            return

        c = []
        write = False
        if self.fgc:
            c.append(str(COLORS[self.fgc]))
            write = True
        if self.bgc:
            c.append(str(COLORS[self.bgc]+10))
            write = True
        if write:
            sys.stdout.write("\033[{}m".format(";".join(c)))

        if not self.gc:
            self.grid_symbol = "+"
        else:
            self.grid_symbol = "\033[{}m{}\033[{}m".format(COLORS[self.gc], "+", COLORS[self.fgc])

    def paint_screen(self) -> None:
        matrix = [[" " for _ in range(self.columns)] for _ in range(int(self.lines))]
        self._move_cursor(1, 1)
        i = 1
        for line in matrix:
            self._move_cursor(1, i)
            sys.stdout.write("".join(line) + "\n")
            i += 1
        sys.stdout.flush()

    def scale(self) -> None:
        if (x_max := int(self.lines / self.rect_ratio)) <= self.columns:
            self.w = x_max
            self.h = self.lines
        else:
            self.w = self.columns
            self.h = int(self.columns * self.rect_ratio)
        self.wm = self.x(0)
        self.hm = self.y(0)

    def clear_matrix(self) -> None:
        self.matrix = [[" " for _ in range(self.w)] for _ in range(int(self.h))]

    def draw_grid(self) -> None:
        for i in range(self.w):
            self.matrix[self.hm][i] = self.grid_symbol
        for i in range(self.h):
            self.matrix[i][self.wm] = self.grid_symbol

    @staticmethod
    def _move_cursor(x: int, y: int) -> None:
        sys.stdout.write(f"\033[{y};{x}H")
        sys.stdout.flush()

    def x(self, x: float) -> int:
        return round((self.w-1) / 2 * (x + 1))

    def y(self, y: float) -> int:
        return round((self.h-1) / 2 * (1 - y))

    def scatter(self, x: t.Union[list, float], y: t.Union[list, float]) -> None:
        if type(x) is list and type(y) is list and (leng := len(x)) == len(y):
            for i in range(leng):
                if abs(y[i]) > 1:
                    continue
                self.matrix[self.y(y[i])][self.x(x[i])] = self.s
        elif type(x) is not list and type(y) is not list:
            self.matrix[self.y(y)][self.x(x)] = self.s  # type: ignore[arg-type]

        elif type(x) is list and type(y) is list and len(x) != len(y):
            raise Exception("Lengths must be the same.")
        else:
            raise Exception("Datatypes must be the same. Both list or int.")

    def show(self) -> None:
        i = 1
        for line in self.matrix:
            self._move_cursor(1, i)
            sys.stdout.write("".join(line) + "\n")
            i += 1
        sys.stdout.flush()

    def animate(self, p: Connection) -> None:
        while True:
            recv = p.recv()  # type: tuple[t.Union[list, int], t.Union[list, int]]
            self.clear_matrix()
            self.scatter(*recv)
            self.show()

    def animate_with_grid(self, p: Connection) -> None:
        while True:
            recv = p.recv()  # type: tuple[t.Union[list, int], t.Union[list, int]]
            self.clear_matrix()
            self.draw_grid()
            self.scatter(*recv)
            self.show()
