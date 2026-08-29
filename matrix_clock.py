#!/usr/bin/env python3
"""A 24-hour seven-segment clock over a Matrix-inspired terminal rain field."""

import curses
import random
import time


FPS = 30
RAIN_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%&*+-<>"
DIGITS = {
    "0": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", " ### ", "#    ", "#    ", "#####"),
    "3": (" ### ", "#   #", "    #", " ### ", "    #", "#   #", " ### "),
    "4": ("#   #", "#   #", "#   #", "#####", "    #", "    #", "    #"),
    "5": ("#####", "#    ", "#    ", " ### ", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    ":": (" ", " ", "#", " ", "#", " ", " "),
}


class Stream:
    def __init__(self, height):
        self.reset(height, random.randint(-height, height))

    def reset(self, height, start=None):
        self.head = start if start is not None else random.randint(-height, 0)
        self.length = random.randint(4, max(5, height // 2))
        self.speed = random.uniform(0.25, 1.1)
        self.tick = 0.0

    def advance(self, height):
        self.tick += self.speed
        if self.tick >= 1:
            self.head += int(self.tick)
            self.tick %= 1
        if self.head - self.length > height:
            self.reset(height)


def safe_add(stdscr, y, x, char, style=0):
    try:
        stdscr.addch(y, x, char, style)
    except curses.error:
        pass


def draw_rain(stdscr, streams, height, width, dim, head):
    for x, stream in enumerate(streams[:width]):
        stream.advance(height)
        for offset in range(stream.length):
            y = stream.head - offset
            if 0 <= y < height:
                style = head if offset == 0 else dim
                safe_add(stdscr, y, x, random.choice(RAIN_CHARS), style)


def clock_lines(value):
    lines = ["" for _ in range(7)]
    for index, symbol in enumerate(value):
        glyph = DIGITS[symbol]
        for row in range(7):
            lines[row] += glyph[row]
            if index != len(value) - 1:
                lines[row] += " "
    return lines


def draw_clock(stdscr, value, height, width, style):
    lines = clock_lines(value)
    clock_width = len(lines[0])
    top = max(0, (height - len(lines)) // 2)
    left = max(0, (width - clock_width) // 2)

    # Paint the clock's bounding box black first so rain never reduces legibility.
    for row, line in enumerate(lines):
        try:
            stdscr.addstr(top + row, left, " " * len(line), curses.color_pair(1))
            for column, char in enumerate(line):
                if char != " ":
                    # The bitmap uses # as a shape marker; render it as a full block
                    # so the clock remains heavy and readable over the animation.
                    safe_add(stdscr, top + row, left + column, "█", style)
        except curses.error:
            pass


def run(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    streams = []
    last_size = None
    frame_time = 1 / FPS

    while True:
        started = time.monotonic()
        height, width = stdscr.getmaxyx()
        if (height, width) != last_size:
            streams = [Stream(height) for _ in range(width)]
            last_size = (height, width)

        stdscr.erase()
        if width < 53 or height < 10:
            message = "Resize terminal to at least 53 x 10"
            safe_add(stdscr, height // 2, max(0, (width - len(message)) // 2), message,
                     curses.color_pair(2) | curses.A_BOLD)
        else:
            draw_rain(stdscr, streams, height, width, curses.color_pair(2) | curses.A_DIM,
                      curses.color_pair(2) | curses.A_BOLD)
            draw_clock(stdscr, time.strftime("%H:%M:%S"), height, width,
                       curses.color_pair(2) | curses.A_BOLD)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 3):
            return
        time.sleep(max(0, frame_time - (time.monotonic() - started)))


if __name__ == "__main__":
    try:
        curses.wrapper(run)
    except KeyboardInterrupt:
        pass
