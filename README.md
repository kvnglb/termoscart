# termoscart
A CLI tool to draw beautiful (animated) curves in the terminal.

![termoscart](https://raw.githubusercontent.com/kvnglb/termoscart/refs/heads/main/images/termoscart.png)

Created with
```
termoscart -r 5000 -l bright-cyan -b black -f 1 -g bright-green lissajous -a 6 -b 7
```

# Usage
```
usage: termoscart [-h] [--settings] [-p <seconds>] [-r <res>]
                  [-R <width/height>] [-s <char>] [-l <color>] [-b <color>]
                  [-g <color>] [-G] [-f <frame>]
                  {lissajous,lissajous2,sine} ...

positional arguments:
  {lissajous,lissajous2,sine}

optional arguments:
  -h, --help            show this help message and exit
  --settings            shows information about the rect-ratio and colors
                        (default: False)
  -p <seconds>, --period <seconds>
                        time in seconds, until the figure finishes 1 cycle
                        (f=1/T) (default: 3)
  -r <res>, --resolution <res>
                        delta between two points (default: 100)
  -R <width/height>, --rect-ratio <width/height>
                        ratio of width/height (depending on the font, needed
                        that a circle appears like a circle and not like an
                        ellipse) (default: 0.5)
  -s <char>, --symbol <char>
                        symbol for the curve (default: '#')
  -l <color>, --line-color <color>
                        color of the curve (default: None)
  -b <color>, --background-color <color>
                        color of the background (default: None)
  -g <color>, --grid-color <color>
                        color of the grid (default: None)
  -G, --grid            enables grid (default: False)
  -f <frame>, --frame <frame>
                        shows the curve at a certain frame without animation,
                        value must be between -1 and 1 (default: None)

LISSAJOUS
usage: termoscart lissajous [-h] [-a <a>] [-b <b>]

x(t, d) = sin(a*t + d), y(t) = sin(b*t)

optional arguments:
  -h, --help  show this help message and exit
  -a <a>      a in the ratio 'a/b' (default: 2)
  -b <b>      b in the ratio 'a/b' (default: 3)

LISSAJOUS2
usage: termoscart lissajous2 [-h] [-b <b>] [-n <n>]

x(t, a) = sin(a*t + d), y(t) = sin(b*t), increase the ratio 'a/b' from 0 to n

optional arguments:
  -h, --help  show this help message and exit
  -b <b>      b in the ratio 'a/b', defines the number of waves (default: 4)
  -n <n>      end for ratio 'a/b' (default: 1)

SINE
usage: termoscart sine [-h] [-A <A>] [-f <f>]

x(t) = t, y(t) = A*sin(2*pi*f*t)

optional arguments:
  -h, --help  show this help message and exit
  -A <A>      amplitude A (default: 1)
  -f <f>      frequency f (default: 1)

```
