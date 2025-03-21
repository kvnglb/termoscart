import os
import sys
import typing as t
from argparse import Namespace
from multiprocessing.connection import Connection

COLOR = {None: 0,
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
    """Print curves to the terminal.

    This class is to compute and print a matrix, that is a visual representation
    of scattered data points.
    The matrix looks like
    [0, 1, 2, 3, 4, ...]
    [0, 1, 2, 3, 4, ...]
    [0, 1, 2, 3, 4, ...]
    [0, 1, 2, 3, 4, ...]
    [...]

    but the data points are allowed in an interval from [-1, 1]. So these points
    are transformed in a way, that point P(0, 0) is in the middle of the matrix
    and not on the top left corner.

    Attributes
    ----------
    rect_ratio : float
        Ratio between width and height. Usually fonts have a smaller space between
        two chars in the same line (row) than two chars in the same column. With
        this setting, one can tune the coordinate system that a circle or square
        does not look distorted like an ellipse or rectangle.
    symbol : char
        The symbol, which is used to print the curves.
    line_color : str
        The foreground-color / the color of the line of the curve.
    background_color : str
        The color of the background of both the line and the coordinate system
        (plot area).
    grid_color : str
        The color of the grid.
    grid_symbol : char
        The symbol, which is used to print the grid.
    columns : int
        The number of the columns of the current terminal.
    rows : int
        The number of the rows -1 of the terminal. One is subtracted, because
        the lowest row should be left empty (otherwise the terminal starts
        scrolling). Well, testing it with lissajous2 and omitting '-1', it
        looks pretty cool in the terminal, when scrolling up again.
    w : int
        The max width, to have a scaled grid / coordinate system (based on
        rect_ratio).
    h : int
        The max height, to have a scaled grid / coordinate system (based on
        rect_ratio).
    wm : int
        The middle of the width of the scaled grid / cooridnate system.
        Used to draw the grid.
    hm : int
        The middle of the height of the scaled grid / cooridnate system.
        Used to draw the grid.
    matrix : list[list]
        This matrix contains the data, that will be plotted. More like, this
        matrix is a representation of the pixels in the terminal, where the
        'symbol' and grid is placed at its respective position. This matrix
        is then printed and the plot becomes visible in the terminal.

    """

    def __init__(self, args: Namespace) -> None:
        """Initialize the class."""
        self.rect_ratio = args.rect_ratio
        self.symbol = args.symbol
        self.line_color = args.line_color
        self.background_color = args.background_color
        self.grid_color = args.grid_color

        size = os.get_terminal_size()
        self.columns = size.columns
        self.rows = size.lines - 1
        self.scale()
        self.clear_matrix()
        self.colorize()

    def colorize(self, reset: bool = False) -> None:
        """Set the line- and background-color for the plot(s).

        This method sets the colors for the line (curve) and the background,
        as well as for the grid. It also resets the colors to the default
        terminal color, when 'True' is passed as argument.

        Parameters
        ----------
        reset, optional
            Reset the terminal's color to its defaults. The default is False.

        """
        if reset:
            sys.stdout.write("\033[0m")
            return

        c = []
        write = False
        if self.line_color:
            c.append(str(COLOR[self.line_color]))
            write = True
        if self.background_color:
            c.append(str(COLOR[self.background_color]+10))
            write = True
        if write:
            sys.stdout.write("\033[{}m".format(";".join(c)))

        if not self.grid_color:
            self.grid_symbol = "+"
        else:
            self.grid_symbol = "\033[{}m{}\033[{}m".format(COLOR[self.grid_color], "+", COLOR[self.line_color])

    def paint_screen(self) -> None:
        """Paint the screen by printing an empty matrix.

        This is useful at the end of the program to erase previously printed
        data points, so to bring the terminal back in a clear state.
        """
        matrix = [[" " for _ in range(self.columns)] for _ in range(int(self.rows))]
        self._move_cursor(1, 1)
        i = 1
        for line in matrix:
            self._move_cursor(1, i)
            sys.stdout.write("".join(line) + "\n")
            i += 1
        sys.stdout.flush()

    def scale(self) -> None:
        """Scale the matrix based on 'rect_ratio'.

        When printing a matrix where all pixels are filled with data points, a
        square will appear rather than a rectangle. This is to ensure that the
        curves are correctly displayed with 1:1 proportions.

        """
        if (x_max := int(self.rows / self.rect_ratio)) <= self.columns:
            self.w = x_max
            self.h = self.rows
        else:
            self.w = self.columns
            self.h = int(self.columns * self.rect_ratio)
        self.wm = self.x(0)
        self.hm = self.y(0)

    def clear_matrix(self) -> None:
        """Remove all data points from the matrix."""
        self.matrix = [[" " for _ in range(self.w)] for _ in range(int(self.h))]

    def draw_grid(self) -> None:
        """Draw a grid in the middle of the plot."""
        for i in range(self.w):
            self.matrix[self.hm][i] = self.grid_symbol
        for i in range(self.h):
            self.matrix[i][self.wm] = self.grid_symbol

    @staticmethod
    def _move_cursor(x: int, y: int) -> None:
        """Move the terminal cursor to the specified position.

        This is needed to create an animation, because the lines get
        overwritten for each new frame. This is more efficient than clearing
        the terminal for every frame of the animation.

        Parameters
        ----------
        x : int
            Row in the terminal.
        y : int
            Column in the terminal.

        """
        sys.stdout.write(f"\033[{y};{x}H")
        sys.stdout.flush()

    def x(self, x: float) -> int:
        """Transform a value in [-1, 1] to their respective column."""
        return round((self.w-1) / 2 * (x + 1))

    def y(self, y: float) -> int:
        """Transform a value in [-1, 1] to their respective row."""
        return round((self.h-1) / 2 * (1 - y))

    def scatter(self, x: t.Union[list, float], y: t.Union[list, float]) -> None:
        """Write a symbol in the matrix at position (x, y)."""
        if type(x) is list and type(y) is list and (leng := len(x)) == len(y):
            for i in range(leng):
                if abs(y[i]) > 1:
                    continue
                self.matrix[self.y(y[i])][self.x(x[i])] = self.symbol
        elif type(x) is not list and type(y) is not list:
            self.matrix[self.y(y)][self.x(x)] = self.symbol  # type: ignore[arg-type]

        elif type(x) is list and type(y) is list and len(x) != len(y):
            raise Exception("Lengths must be the same.")
        else:
            raise Exception("Datatypes must be the same. Both list or int.")

    def show(self) -> None:
        """Print the matrix to the terminal, starting in the top left corner."""
        i = 1
        for line in self.matrix:
            self._move_cursor(1, i)
            sys.stdout.write("".join(line) + "\n")
            i += 1
        sys.stdout.flush()

    def animate(self, p: Connection) -> None:
        """Print the matrix with the newly received data points to the terminal."""
        while True:
            recv = p.recv()  # type: tuple[t.Union[list, int], t.Union[list, int]]
            self.clear_matrix()
            self.scatter(*recv)
            self.show()

    def animate_with_grid(self, p: Connection) -> None:
        """Behave as animate, but also print the grid to the terminal."""
        while True:
            recv = p.recv()  # type: tuple[t.Union[list, int], t.Union[list, int]]
            self.clear_matrix()
            self.draw_grid()
            self.scatter(*recv)
            self.show()
