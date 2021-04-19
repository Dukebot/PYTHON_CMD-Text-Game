import curses
import sys
import math
from os import system, name

# Borrowed almost all of the code from here http://adamlamers.com/post/FTPD9KNRA8CT

class CursesMenu(object):

    def __init__(self, menu_options):
        self.screen = curses.initscr()
        self.menu_options = menu_options
        self.selected_option = 0
        self._previously_selected_option = None
        self.running = True

        #init curses and curses input
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.curs_set(0) #Hide cursor
        self.screen.keypad(1)

        #set up color pair for highlighted option
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.hilite_color = curses.color_pair(1)
        self.normal_color = curses.A_NORMAL

        # Last element height
        self.last_height = 0

    def prompt_selection(self, parent=None):

        option_count = len(self.menu_options['options'])

        input_key = None

        ENTER_KEY = ord('\n')
        while input_key != ENTER_KEY:
            if self.selected_option != self._previously_selected_option:
                self._previously_selected_option = self.selected_option

            self.screen.border(0)
            self._draw_title()
            for option in range(option_count):
                if self.selected_option == option:
                    self._draw_option(option, self.hilite_color)
                else:
                    self._draw_option(option, self.normal_color)

            max_y, max_x = self.screen.getmaxyx()
            if input_key is not None:
                self.screen.addstr(max_y-3, max_x - 5, "{:3}".format(self.selected_option))
            self.screen.refresh()


            input_key = self.screen.getch()
            down_keys = [curses.KEY_DOWN, ord('j')]
            up_keys = [curses.KEY_UP, ord('k')]
            exit_keys = [ord('q')]

            if input_key in down_keys:
                if self.selected_option < option_count - 1:
                    self.selected_option += 1
                else:
                    self.selected_option = 0

            if input_key in up_keys:
                if self.selected_option > 0:
                    self.selected_option -= 1
                else:
                    self.selected_option = option_count - 1

            if input_key in exit_keys:
                self.selected_option = option_count #auto select exit and return
                break

        return self.selected_option

    def _draw_option(self, option_number, style):
        self.screen.addstr(self.last_height + 2 + option_number,
                           4,
                           "{}".format(self.menu_options['options'][option_number]['title']),
                           style)

    def _fit_words(self,y,x,str,opt):
        str = str.replace('\n', ' \n ')
        self.last_height = y
        words = str.split(' ')
        max_y, max_x = self.screen.getmaxyx()
        line_length = max_x - 4 - x

        buffer = ""
        lines = []
        for word in words:
            if word == '\n':
                lines.append(buffer)
                buffer = ""
                continue
            if len(buffer) + len(word) + 1 > line_length:
                lines.append(buffer)
                buffer = ""
            if buffer != "":
                buffer += " "
            buffer += word
        lines.append(buffer)

        for line in lines:
            self.last_height += 1
            self.screen.addstr(self.last_height, x, line,opt)

    def _draw_title(self):
        self.screen.addstr(2, 2, self.menu_options['title'], curses.A_STANDOUT)
        self._fit_words(4, 2, self.menu_options['subtitle'], curses.A_BOLD)

    def display(self):
        selected_option = self.prompt_selection()
        curses.endwin()
        self.screen.clear()
        if selected_option < len(self.menu_options['options']):
            selected_opt = self.menu_options['options'][selected_option]
            return selected_opt
