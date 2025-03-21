import math
import typing as t
from argparse import Namespace, _SubParsersAction


class Parser:
    """Add the parsers to the subparser for the respective curve method.

    Attributes
    ----------
    _subparser : argparse._SubParsersAction
        The subparser, which contains all the parsers for the respective curve method (Must
        start with an underscore to skip the calling on initialization).

    """

    def __init__(self, subparser: _SubParsersAction):
        """Call all methods, which will add a parser for their respective computation method."""
        self._subparser = subparser
        for method_name in dir(self):
            if callable(getattr(self, method_name)) and not method_name.startswith("_"):
                getattr(self, method_name)()

    def sine(self) -> None:
        """Add parser for the sine wave."""
        parser = self._subparser.add_parser("sine", description="x(t) = t, y(t) = A*sin(2*pi*f*t)")
        parser.add_argument("-A", metavar="<A>", type=float, default=1, help="amplitude A (default: %(default)s)")
        parser.add_argument("-f", metavar="<f>", type=float, default=1, help="frequency f (default: %(default)s)")

    def lissajous(self) -> None:
        """Add parser for the lissajous curve."""
        parser = self._subparser.add_parser("lissajous", description="x(t, d) = sin(a*t + d), y(t) = sin(b*t)")
        parser.add_argument("-a", metavar="<a>", type=float, default=2, help="a in the ratio 'a/b' (default: %(default)s)")
        parser.add_argument("-b", metavar="<b>", type=float, default=3, help="b in the ratio 'a/b' (default: %(default)s)")

    def lissajous2(self) -> None:
        """Add parser for the second lissajous curve."""
        parser = self._subparser.add_parser("lissajous2", description="x(t, a) = sin(a*t + d), y(t) = sin(b*t), increase the ratio 'a/b' from 0 to n")
        parser.add_argument("-b", metavar="<b>", type=float, default=4, help="b in the ratio 'a/b', defines the number of waves (default: %(default)s)")
        parser.add_argument("-n", metavar="<n>", type=int, default=1, help="end for ratio 'a/b' (default: %(default)s)")


class F:
    """Calculate the values to display the animation.

    This class is needed to calculate the X- and Y-values of the animation in the
    terminal. When this class is initialized, all parsers are added to the subparser,
    where the curve to display can be chosen. Calling the resulting object will return
    the function to calculate the values for the curve.

    All these function must take one argument. This argument will move in the
    interval [-1, 1) to create the single frames.

    Attributes
    ----------
    parser : argparse._SubParsersAction
        The class containing the subparser, which contains all parsers for all curves.
    args : argparse.Namespace
        The namespace with all availables arguments (from both, the main parser
        and all parsers from the subparser).
    x : list[float]
        The list to draw the curve from x=-1 to x=1.

    Other attributes are specified in the method's respective computation
    or _const function.

    """

    def __init__(self, subparser: _SubParsersAction) -> None:
        """Add the parsers with the needed arguments for the respective curve."""
        self.parser = Parser(subparser)

    def __call__(self, args: Namespace) -> t.Callable:
        """Return the method to calculate the curve. Also calculate the needed constants."""
        self.args = args
        self.x = [x / self.args.resolution for x in range(-self.args.resolution, self.args.resolution+1)]
        if not args.curve:
            choices = []
            for choice in self.parser._subparser.choices:
                choices.append(choice)
            raise ValueError("Choose from {}".format(", ".join([f"'{c}'" for c in choices])))
        else:
            calc_const = getattr(self, "{}_{}".format(self.args.curve, "const"), None)
            if calc_const:
                calc_const()
            return getattr(self, self.args.curve)

    def sine(self, w: int) -> tuple[list[float], list[float]]:
        """Calculate a simple sine wave moving through the terminal."""
        y = [self.args.A * math.sin(self.args.f*(x+w) * math.pi) for x in self.x]
        return self.x, y

    def lissajous_const(self) -> None:
        """Calculate the constant for Y for the lissajous methods."""
        self.y = [math.sin(self.args.b * x * math.pi) for x in self.x]

    def lissajous(self, w: int) -> tuple[list[float], list[float]]:
        """Calculate X for the lissajous curves emulating slightly detuned frequencies."""
        x = [math.sin((self.args.a*x + w) * math.pi) for x in self.x]
        return x, self.y

    def lissajous2_const(self) -> None:
        """Call the method to calculate the contants for the lissajous2 method."""
        self.lissajous_const()

    def lissajous2(self, w: int) -> tuple[list[float], list[float]]:
        """Calculate X for the lissajous curves when increasing the ratio 'a/b'."""
        x = [math.sin(self.args.n/2*(w+1)*self.args.b * x * math.pi) for x in self.x]
        return x, self.y
