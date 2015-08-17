import curses
import textwrap
from curses import wrapper

class StdinWindow:
    def __init__(self):
        h, w = 4, 10
        px = (curses.COLS - w) // 2
        py = (curses.LINES - h) // 2

        self.win = curses.newwin(h, w, py, px)
        self.h, self.w = self.win.getmaxyx()
        self.active = False
        self.formatstr = ' {:^' + str(self.w - 3) + '}'

    def refresh(self):
        if self.active:
            self.win.clear()
            self.win.addstr(1, 1, self.formatstr.format('input:'), curses.A_REVERSE)
            self.win.addstr(2, 1, self.formatstr.format(' '), curses.A_REVERSE)
            self.win.refresh()

class StdoutWindow:
    def __init__(self):
        h, w = 10, 30
        px = (curses.COLS - w) // 2
        py = (curses.LINES - h) // 2

        self.win = curses.newwin(h, w, py, px)
        self.h, self.w = self.win.getmaxyx()
        self.active = False
        self.start_l = 0

    def shift_up(self, amt = 1):
        if self.start_l - amt >= 0:
            self.start_l -= amt

    def shift_down(self, stdout, amt = 1):
        if self.start_l + self.h - 2 + amt <= len(textwrap.wrap(stdout, self.w - 2)): 
            self.start_l += amt

    def change_active(self):
        if self.active:
            self.active = False
        else:
            self.active = True

    def refresh(self, stdout):
        if self.active:
            self.win.clear()
            self.win.border()
            self.win.addstr((' {:^' + str(self.w - 1) + '}').format('stdout'), curses.A_REVERSE)
            to_write = textwrap.wrap(stdout, self.w - 2)
            t_w_l = len(to_write)
            for h in range(self.h - 2):
                if h + self.start_l < t_w_l:
                    self.win.addstr(h + 1, 1, to_write[h + self.start_l])

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

    def display_regs(self, regs, c_reg):
        c_shift = 0
        c_width = 16
        i = self.start_r
        while i < 32:
            if c_shift + c_width > self.cols:
                break
            line = '${0:<2} = {1:<8}'.format(i, regs[i].hex)
            if c_reg == i:
                self.win.addstr(i % self.r_p_c + 1, 1 + c_shift, line, curses.color_pair(1))
            else:
                self.win.addstr(i % self.r_p_c + 1, 1 + c_shift, line)
            
            i += 1
            if i % self.r_p_c == 0:
                c_shift += c_width

    def shift_right(self):
        if self.start_r + self.r_p_c < 32:
            self.start_r += self.r_p_c

    def shift_left(self):
        if self.start_r > 0:
            self.start_r -= self.r_p_c

    def refresh(self, regs, c_reg):
        self.win.clear()
        self.win.border()
        self.display_regs(regs, c_reg)
        self.win.refresh()

class MemWindow:
    def __init__(self):
        pt = 1
        pb = 10
        px = 5
        h, w = curses.LINES - (pt + pb), curses.COLS - (px * 2)
        self.col_str = '| {0:<3} | {1:<10} | {2:<10} | {3:<'+ str(w) +'} |'

        self.win = curses.newwin(h - 1, w - 1, pt, px)
        self.lines, self.cols = self.win.getmaxyx()
        self.start_i = 0 # TODO: might need to adjust for starting ind

    def shift_up(self, amt = 1):
        if self.start_i - amt >= 0:
            self.start_i -= amt

    def shift_down(self, maxlen, amt = 1):
        if self.start_i + self.lines - 3 + amt <= maxlen:
            self.start_i += amt

    def draw_cols(self, pc, mem, memlen, c_mem):
        pc_i = pc // 4
        for i in range(self.start_i, min(self.lines - 3 + self.start_i, memlen)):
            if pc_i == i:
                pc_p = '->'
            else:
                pc_p = ''
            line = self.col_str.format(pc_p, hex(i * 4), mem[i].hex, mem[i].bin)[:self.cols]
            if c_mem == i:
                self.win.addstr(1 + i - self.start_i, 0, line, curses.color_pair(1))
            else:
                self.win.addstr(1 + i - self.start_i, 0, line)

    def refresh(self, pc, mem, memlen, c_mem):
        title_str = self.col_str.format('pc', 'addr', 'hex', 'bin')[:self.cols]

        self.win.clear()
        self.win.addstr(0, 0, title_str, curses.A_REVERSE)
        self.draw_cols(pc, mem, memlen, c_mem)
        self.win.addstr(self.lines - 2, 0, title_str, curses.A_REVERSE)
        self.win.refresh()

class Window:
    def __init__(self, screen):
        if curses.LINES < 30 or curses.COLS < 30:
            raise Exception('ERROR: terminal window too small for debugger')
        self.scr = screen
        self.mem_window = MemWindow()
        self.reg_window = RegWindow()
        self.out_window = StdoutWindow()
        self.in_window = StdinWindow()

        # for coloring, gets adjusted in execute() of the fec
        self.c_mem = -1
        self.c_reg = -1
        curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        # for stdout
        self.stdout = ''

    def reset_changed(self):
        self.c_mem = -1
        self.c_reg = -1

    def get_inp(self):
        # might not need the whole refresh
        self.scr.erase()
        self.scr.refresh()
        self.in_window.active = True
        self.in_window.refresh()
        c = self.scr.getkey()
        self.in_window.active = False
        return c

    def print_stdout(self, out):
        self.stdout += out

    def tick(self, pc, mem, regs):
        memlen = len(mem) 
        while True:
            self.scr.erase()
            self.scr.refresh()
            self.mem_window.refresh(pc, mem, memlen, self.c_mem)
            self.reg_window.refresh(regs, self.c_reg)
            self.out_window.refresh(self.stdout)
            self.in_window.refresh()

            c = self.scr.getch()
            if c == ord('q'): 
                return 'q'
            elif c == 27: # esc or alt
                self.scr.nodelay(True)
                n = self.scr.getch()
                if n == -1:
                    return 'q'
                self.scr.nodelay(False)
            elif c == curses.KEY_UP or c == curses.KEY_PPAGE:
                amt = 1
                if c == curses.KEY_PPAGE:
                    amt = 5

                if self.out_window.active:
                    self.out_window.shift_up(amt)
                else:
                    self.mem_window.shift_up(amt)
            elif c == curses.KEY_DOWN or c == curses.KEY_NPAGE:
                amt = 1
                if c == curses.KEY_NPAGE:
                    amt = 5

                if self.out_window.active:
                    self.out_window.shift_down(self.stdout, amt)
                else:
                    self.mem_window.shift_down(memlen, amt)
            elif c == curses.KEY_RIGHT:
                self.reg_window.shift_right()
            elif c == curses.KEY_LEFT:
                self.reg_window.shift_left()
            elif c == ord('s'):
                self.out_window.change_active()
            elif c == ord(' ') or c == ord('n'):
                return ' '
            

def setup_and_call_fec(machine, start):
    wrapper(machine.fetch_execute_cycle, start) # to send the screen back