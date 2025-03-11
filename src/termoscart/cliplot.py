import os
import sys
import typing as t
from multiprocessing import Process
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
    def __init__(self, rect_ratio: float, fgc: str, bgc: str, s: str) -> None:
        self.rect_ratio = rect_ratio
        self.s = s
        self._colorize(fgc, bgc)

        size = os.get_terminal_size()
        self.columns = size.columns
        self.lines = size.lines - 1
        self.scale()
        self.x = lambda x: round((self.w-1) / 2 * (x + 1))
        self.y = lambda y: round((self.h-1) / 2 * (1 - y))
        self.paint_screen()
        self.clear_matrix()

    @staticmethod
    def _colorize(fgc: t.Union[str, None] = None, bgc: t.Union[str, None] = None) -> None:
        sys.stdout.write("\033[{};{}m".format(COLORS[fgc], COLORS[bgc]+10))

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

    def clear_matrix(self) -> None:
        self.matrix = [[" " for _ in range(self.w)] for _ in range(int(self.h))]

    @staticmethod
    def _move_cursor(x: int, y: int) -> None:
        sys.stdout.write(f"\033[{y};{x}H")
        sys.stdout.flush()

    def scatter(self, x: t.Union[list, int], y: t.Union[list, int], s: str) -> None:
        if type(x) is list and type(y) is list and (leng := len(x)) == len(y):
            for i in range(leng):
                if abs(y[i]) > 1:
                    continue
                self.matrix[self.y(y[i])][self.x(x[i])] = s
        elif type(x) is not list and type(y) is not list:
            self.matrix[self.y(y)][self.x(x)] = s

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
        def loop(p: Connection) -> None:
            while True:
                recv = p.recv()  # type: tuple[t.Union[list, int], t.Union[list, int]]
                self.clear_matrix()
                self.scatter(*recv, self.s)
                self.show()
        self.proc = Process(target=loop, args=(p,), daemon=True)
        self.proc.start()
