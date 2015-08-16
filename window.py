import curses
from curses import A_BLINK
from curses import wrapper

class DataWindow:
    def __init__(self):
        py, px = 1, 5
        h, w = curses.LINES - (py * 2), curses.COLS - (px * 2)
        self.col_str = '| {0:<3} | {1:<10} | {2:<10} | {3:<'+ str(w - 23) +'} |'

        self.win = curses.newwin(h - 1, w - 1, py, px)
        self.lines, self.cols = self.win.getmaxyx()
        self.start_i = 5 # TODO: might need to adjust for starting ind

    def shift_up(self):
        if self.start_i > 0:
            self.start_i -= 1

    def shift_down(self):
        if self.start_i + self.lines - 3 < 100:
            self.start_i += 1

    def draw_cols(self):
        for i in range(self.start_i, self.lines - 3 + self.start_i):
            self.win.addstr(1 + i - self.start_i, 0, self.col_str.format(str(i), '0', '0', '0')[:self.cols])

    def refresh(self):
        title_str = self.col_str.format('pc', 'addr', 'hex', 'bin')[:self.cols]

        self.win.clear()
        self.win.addstr(0, 0, title_str, curses.A_REVERSE)
        self.draw_cols()
        self.win.addstr(self.lines - 2, 0, title_str, curses.A_REVERSE)
        self.win.refresh()

data = [['->', i, '', ''] for i in range(3000)]

# def refresh(scr):
#     scr.clear()
#     scr.addstr(py, px, col_str.format('pc', 'addr', 'hex', 'bin')[:w],curses.A_REVERSE)
#     #for i in range(start, height - 2 + start - 1):
#     #    win.addstr(i - start + 1, 0, col_str.format(data[i][0], data[i][1], data[i][2], data[i][3])[:width])
#     scr.addstr(h - 2, px, col_str.format('pc', 'addr', 'hex', 'bin')[:w],curses.A_REVERSE)
#     scr.refresh()

def main(scr):
    data_window = DataWindow()

    while True:
        scr.erase()
        scr.refresh()
        data_window.refresh()

        c = scr.getch()
        if c == ord('q'): 
            break
        elif c == 27: # esc or alt
            scr.nodelay(True)
            n = scr.getch()
            if n == -1:
                break
            scr.nodelay(False)
        elif c == curses.KEY_UP:
            data_window.shift_up()
        elif c == curses.KEY_DOWN:
            data_window.shift_down()
        elif c == curses.KEY_RIGHT:
            pass

wrapper(main)