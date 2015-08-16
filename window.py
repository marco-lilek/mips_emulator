import curses
from curses import wrapper

# This one will be just like a popup
class StdinWindow:
    def __init__(self):
        h, w = 5, 8
        px = (curses.COLS - w) // 2
        py = (curses.LINES - h) // 2

        self.win = curses.newwin(h, w, py, px)
        self.h, self.w = self.win.getmaxyx()
        self.active = True
        self.formatstr = ' {:^' + str(self.w - 1) + '}'

    def refresh(self):
        if self.active:
            self.win.clear()
            self.win.addstr(0, 0, self.formatstr.format(' '), curses.A_REVERSE)
            self.win.addstr(1, 0, self.formatstr.format('input:'), curses.A_REVERSE)
            self.win.addstr(2, 0, self.formatstr.format(' '), curses.A_REVERSE)
            self.win.refresh()

class StdoutWindow:
    def __init__(self):
        h, w = 10, 30
        px = (curses.COLS - w) // 2
        py = (curses.LINES - h) // 2

        self.win = curses.newwin(h, w, py, px)
        self.h, self.w = self.win.getmaxyx()
        self.active = False

    def change_active(self):
        if self.active:
            self.active = False
        else:
            self.active = True

    def refresh(self):
        if self.active:
            self.win.clear()
            self.win.border()
            self.win.addstr((' {:^' + str(self.w - 1) + '}').format('stdout'), curses.A_REVERSE)
            self.win.refresh()

class RegWindow:
    def __init__(self):
        pt = curses.LINES - 12
        px = 5
        h, w = 10, curses.COLS - (px * 2)
        self.win = curses.newwin(h - 2, w - 1, pt, px)
        self.lines, self.cols = self.win.getmaxyx()
        self.start_r = 0
        self.r_p_c = self.lines - 2 # regs per col

    def display_regs(self):
        c_shift = 0
        c_width = 16
        i = self.start_r
        while i < 32:
            if c_shift + c_width > self.cols:
                break
            self.win.addstr(i % self.r_p_c + 1, 1 + c_shift, '${0:<2} = {1:<8}'.format(i, 10))
            i += 1
            if i % self.r_p_c == 0:
                c_shift += c_width

    def shift_right(self):
        if self.start_r + self.r_p_c < 32:
            self.start_r += self.r_p_c

    def shift_left(self):
        if self.start_r > 0:
            self.start_r -= self.r_p_c

    def refresh(self):
        self.win.clear()
        self.win.border()
        self.display_regs()
        self.win.refresh()

class MemWindow:
    def __init__(self):
        pt = 1
        pb = 10
        px = 5
        h, w = curses.LINES - (pt + pb), curses.COLS - (px * 2)
        self.col_str = '| {0:<3} | {1:<10} | {2:<10} | {3:<10} | {4:<'+ str(w) +'} |'

        self.win = curses.newwin(h - 1, w - 1, pt, px)
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
            self.win.addstr(1 + i - self.start_i, 0, self.col_str.format(str(i), '0', '0', '0', 's')[:self.cols])

    def refresh(self):
        title_str = self.col_str.format('pc', 'addr', 'src', 'hex', 'bin')[:self.cols]

        self.win.clear()
        self.win.addstr(0, 0, title_str, curses.A_REVERSE)
        self.draw_cols()
        self.win.addstr(self.lines - 2, 0, title_str, curses.A_REVERSE)
        self.win.refresh()

def debugger_main(scr):
    if curses.LINES < 30 or curses.COLS < 30:
        raise Exception('ERROR: terminal window too small for debugger')
    mem_window = MemWindow()
    reg_window = RegWindow()
    out_window = StdoutWindow()
    in_window = StdinWindow()

    while True:
        scr.erase()
        scr.refresh()
        mem_window.refresh()
        reg_window.refresh()
        out_window.refresh()
        in_window.refresh()

        if in_window.active:
            c = scr.getkey()
            in_window.active = False
            continue # TODO fix

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
            mem_window.shift_up()
        elif c == curses.KEY_DOWN:
            mem_window.shift_down()
        elif c == curses.KEY_RIGHT:
            reg_window.shift_right()
        elif c == curses.KEY_LEFT:
            reg_window.shift_left()
        elif c == ord('s'):
            out_window.change_active()

        # space is for step

wrapper(debugger_main)