# ASCII Art Terminal Clock

A 24-hour ASCII art clock for the terminal, displayed in bright green over a black, Matrix-inspired falling-character background. The application targets a standard 80×24 terminal, redraws at 30 frames per second, and responds to terminal resizing.

## Running the clock

The project uses only Python's standard library, so no packages need to be installed.

```bash
./matrix_clock.py
```

You can also run it with Python directly:

```bash
python3 matrix_clock.py
```

Press `q`, `Q`, or `Ctrl-C` to exit. The clock needs a terminal of at least 53 columns by 10 rows; an 80×24 window gives it the intended composition.

## How it works

The program uses Python's `curses` module. `curses` provides control over terminal cursor placement, colours, keyboard input, and screen redraws without scrolling the terminal like a normal command-line program would.

At its core, the application runs a frame loop at 30 FPS:

```text
read the terminal size
clear the previous frame
advance and draw the falling-character streams
read the current time as HH:MM:SS
draw a black backing behind the clock
draw the bright-green clock digits
present the completed frame
```

This produces animation while keeping the time updated every second.

## Clock rendering

Each digit is represented by a seven-row bitmap in the `DIGITS` dictionary. For example, the `0` is stored as a small grid of characters:

```text
 ### 
#   #
#   #
#   #
#   #
#   #
 ### 
```

The `#` characters are only shape markers in the source. During rendering, every non-space marker becomes a solid `█` character in bright green. This gives the clock a heavier, more legible appearance than a thin ASCII outline.

The current time is formatted with `time.strftime("%H:%M:%S")`, which guarantees a 24-hour display with leading zeroes. The renderer combines the glyphs for all eight characters, including the two colons, then calculates its left and top offsets so the finished clock remains centred.

## Matrix rain background

The background is made from one independent stream for each terminal column. A stream has four pieces of state:

| Property | Purpose |
| --- | --- |
| `head` | The current row of the stream's leading character. |
| `length` | How many rows of trailing characters the stream contains. |
| `speed` | Its randomized movement rate. |
| `tick` | Fractional progress used to produce varied speeds. |

On each frame, streams advance down the terminal and draw random characters from a small alphabet of letters, digits, and symbols. The leading character is rendered in bold green, while trailing characters use a dim green style. When an entire stream moves below the bottom of the terminal, it is reset above the visible area with a new random length and speed.

The result is a continuously changing field rather than a pre-rendered animation.

## Layering and readability

The clock is rendered after the rain. Before placing its bright-green blocks, the program draws a black rectangle the same size as the clock's text grid. This masks the background directly behind the digits, maintaining strong contrast and making the time readable even with dense animation elsewhere on screen.

The terminal colour setup uses a black background and a green foreground. `A_BOLD` is applied to the clock and rain heads, while `A_DIM` is used for the rain trails.

## Resizing and input

At the start of every frame, the program compares the current terminal dimensions with the previous dimensions. If they differ, it rebuilds the list of rain streams to match the new number of columns. The clock is then re-centred automatically.

Keyboard input is non-blocking, so checking for a quit key does not pause the animation. This is what allows smooth movement while the application remains interactive.

## Project files

| File | Description |
| --- | --- |
| `matrix_clock.py` | The complete terminal clock application. |
| `README.md` | Short installation and usage guide. |
| `ASCII-Art-Terminal-Clock.md` | This implementation guide. |
