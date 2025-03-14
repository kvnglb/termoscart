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
        parser = self._subparser.add_parser("sine")
        parser.add_argument("-A", type=float, default=1)
        parser.add_argument("-a", type=float, default=1)

    def lissajous(self) -> None:
        parser = self._subparser.add_parser("lissajous")
        parser.add_argument("-a", type=float, default=2)
        parser.add_argument("-b", type=float, default=3)

    def lissajous2(self) -> None:
        parser = self._subparser.add_parser("lissajous2")
        parser.add_argument("-n", type=float, default=1)


class F:
    def __init__(self, subparser: _SubParsersAction) -> None:
        self.parser = Subparser(subparser)

    def __call__(self, args: Namespace) -> t.Callable:
        self.args = args
        self.x = [x / self.args.N for x in range(-self.args.N, self.args.N+1)]
        if not args.curve:
            choices = []
            for choice in self.parser._subparser.choices:
                choices.append(choice)
            raise ValueError("Choose from {}".format(", ".join([f"'{c}'" for c in choices])))
        else:
            return getattr(self, self.args.curve)

    def sine(self, w: int) -> tuple[list[float], list[float]]:
        y = [self.args.A * math.sin(self.args.a*(x+w) * math.pi) for x in self.x]
        return self.x, y

    def lissajous(self, w: int) -> tuple[list[float], list[float]]:
        x = [math.sin((self.args.a*x + w) * math.pi) for x in self.x]
        y = [math.sin(self.args.b * x * math.pi) for x in self.x]
        return x, y

    def lissajous2(self, w: int) -> tuple[list[float], list[float]]:
        x = [math.sin((w+1)*self.args.n * x * math.pi) for x in self.x]
        y = [math.sin(2*self.args.n * x * math.pi) for x in self.x]
        return x, y
