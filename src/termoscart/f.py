import math
import typing as t
from argparse import Namespace, _SubParsersAction


class Subparser:
    def __init__(self, subparser: _SubParsersAction):
        self._subparser = subparser
        for method_name in dir(self):
            if callable(getattr(self, method_name)) and not method_name.startswith("_"):
                getattr(self, method_name)()

    def sine(self) -> None:
        parser = self._subparser.add_parser("sine", description="x(t) = t, y(t) = A*sin(2*pi*f*t)")
        parser.add_argument("-A", metavar="<A>", type=float, default=1, help="amplitude A (default: %(default)s)")
        parser.add_argument("-f", metavar="<f>", type=float, default=1, help="frequency f (default: %(default)s)")

    def lissajous(self) -> None:
        parser = self._subparser.add_parser("lissajous", description="x(t, d) = sin(a*t + d), y(t) = sin(b*t)")
        parser.add_argument("-a", metavar="<a>", type=float, default=2, help="a in the ratio 'a/b' (default: %(default)s)")
        parser.add_argument("-b", metavar="<b>", type=float, default=3, help="b in the ratio 'a/b' (default: %(default)s)")

    def lissajous2(self) -> None:
        parser = self._subparser.add_parser("lissajous2", description="x(t, a) = sin(a*t + d), y(t) = sin(b*t), increase the ratio 'a/b' from 0 to n")
        parser.add_argument("-b", metavar="<b>", type=float, default=4, help="b in the ratio 'a/b', defines the number of waves (default: %(default)s)")
        parser.add_argument("-n", metavar="<n>", type=int, default=1, help="end for ratio 'a/b' (default: %(default)s)")


class F:
    def __init__(self, subparser: _SubParsersAction) -> None:
        self.parser = Subparser(subparser)

    def __call__(self, args: Namespace) -> t.Callable:
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
        y = [self.args.A * math.sin(self.args.f*(x+w) * math.pi) for x in self.x]
        return self.x, y

    def lissajous_const(self):
        self.y = [math.sin(self.args.b * x * math.pi) for x in self.x]

    def lissajous(self, w: int) -> tuple[list[float], list[float]]:
        x = [math.sin((self.args.a*x + w) * math.pi) for x in self.x]
        return x, self.y

    def lissajous2_const(self):
        self.y = [math.sin(self.args.b * x * math.pi) for x in self.x]

    def lissajous2(self, w: int) -> tuple[list[float], list[float]]:
        x = [math.sin(self.args.n/2*(w+1)*self.args.b * x * math.pi) for x in self.x]
        return x, self.y
