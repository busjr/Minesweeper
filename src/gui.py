import os
import random
import time
from os import name
from setting import *
import customtkinter as ct

__version__ = "v0.1"

class MinesweeperGameLogic:
    def __init__(self, column, line, bomb, first_click_pos):
        self.column = column
        self.line = line
        self.bomb = bomb
        self.first_click_pos = first_click_pos

    def make_matrix(column, line, bomb, first_click_pos):
        # the way the numbers are added around the bomb when it is created
        matrix = [[0] * column for i in range(line)]

        placed = 0
        while placed < bomb:
            RNLINE = random.randint(0, line-1)
            RNCOLUMN = random.randint(0, column-1)
            FCPline, FCPcolumn = first_click_pos

            if (matrix[RNLINE][RNCOLUMN] == "*") or (RNLINE == FCPline and RNCOLUMN == FCPcolumn):
                continue  # if the bomb is already there or it is the first click position

            matrix[RNLINE][RNCOLUMN] = "*"

            placed += 1
            neighbors = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (-1, 1), (1, -1)]

            for matrix_row, matrix_column in neighbors:
                neighbor_row = RNLINE + matrix_row
                neighbor_column = RNCOLUMN + matrix_column
                if (0 <= neighbor_row < line and 0 <= neighbor_column < column):
                        if isinstance(matrix[neighbor_row][neighbor_column], int): 
                            matrix[neighbor_row][neighbor_column] += 1

        return matrix

class App(ct.CTk):
    def __init__(self):
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - APP_WINDOW_WIDTH) // 2
        y = (screen_height - APP_WINDOW_HEIGHT) // 2

        self.geometry(f"{APP_WINDOW_WIDTH}x{APP_WINDOW_HEIGHT}+{x}+{y}")
        self.title(f"Minesweeper {__version__} (by busjr)")
        if name == "nt":
            ico_path = os.path.join(os.path.dirname(__file__), ICON_PATH)
            self.iconbitmap(ico_path)
        self.resizable(False, False)

        self.btn_open_classic = ct.CTkButton(
            master=self, 
            fg_color=FG_COLOR_BTN,
            hover_color=HOVER_COLOR_BTN,
            border_width=BORDER_WIDTH_BTN,
            width=GAME_CLASSIC_WIDTH_BTN,
            height=GAME_CLASSIC_HEIGHT_BTN,
            text=GAME_CLASSIC_TEXT, 
            command=lambda: self.open_second_window(width=288, height=318, column=9, line=9, bomb=10)
        )
        self.btn_open_classic.grid(row=0, column=0, pady=5, padx=5)

        self.btn_open_medium = ct.CTkButton(
            master=self, 
            fg_color=FG_COLOR_BTN,
            hover_color=HOVER_COLOR_BTN,
            border_width=BORDER_WIDTH_BTN,
            width=GAME_CLASSIC_WIDTH_BTN,
            height=GAME_CLASSIC_HEIGHT_BTN,
            text=GAME_MEDIUM_TEXT, 
            command=lambda: self.open_second_window(width=512, height=543, column=16, line=16, bomb=40)
        )
        self.btn_open_medium.grid(row=1, column=0, pady=5, padx=5)

    def open_second_window(self, width, height, column, line, bomb):
        self.withdraw()  # hide the main (App) window
        self.second_window = MinesweeperGameGUI(self, width, height, column, line, bomb)  # pass a link to the main window (App)

class MinesweeperGameGUI(ct.CTkToplevel):
    def __init__(self, main_window, width, height, column, line, bomb):
        super().__init__()
        self.main_window = main_window
        self.width = width
        self.height = height
        self.column = column
        self.line = line
        self.bomb = bomb
        self.total_cell = column * line
        self.buttons = []
        self.bombs = [] 
        self.opened = set()
        self.first_click_done = False
        self.game_win = False
        self.game_loss = False

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.title(f"Minesweeper {__version__} (by busjr)")
        if name == "nt":
            ico_path = os.path.join(os.path.dirname(__file__), ICON_PATH)
            self.after(250, lambda: self.wm_iconbitmap(ico_path))
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        self.text_time = ct.CTkLabel(
            master=self,
            height=HEIGHT_LABEL_TIME,
            width=WIDTH_LABEL_TIME,
            fg_color=FG_COLOR_LABEL,
            text="00:00:00"
        )
        self.text_time.grid(row=0, column=0, columnspan=column, sticky='w')

        self.text_status = ct.CTkLabel(
            master=self,
            height=HEIGHT_LABEL_STATUS,
            width=WIDTH_LABEL_STATUS,
            corner_radius=CORNER_RADIUS_LABEL_STATUS,
            fg_color=FG_COLOR_LABEL,
            text="(-_-)"
        )
        self.text_status.grid(row=0, column=0, columnspan=column, padx=10)

        self.btn_back = ct.CTkButton(
            master=self, 
            height=HEIGHT_BTN_BACK, 
            width=WIDTH_BTN_BACK, 
            fg_color=FG_COLOR_BTN, 
            hover_color=HOVER_COLOR_BTN, 
            corner_radius=CORNER_RADIUS_BTN,
            text=TEXT_BTN_BACK, 
            command=self.close_window
        )
        self.btn_back.grid(row=0, column=0, columnspan=column, sticky='e')

        for i in range(column * line):
            row = i // column
            col = i % column

            button = ct.CTkButton(
                master=self,
                height=HEIGHT_BTN,
                width=WIDTH_BTN,
                fg_color=FG_COLOR_BTN,
                hover_color=HOVER_COLOR_BTN,
                border_width=BORDER_WIDTH_BTN,
                corner_radius=CORNER_RADIUS_BTN,
                state="normal",
                text="",
            )
            self.buttons.append(button)
            button.grid(row=row + 2, column=col, padx=1, pady=1)
            button.bind("<Button-1>", lambda event, r=row, c=col: self.button_callback(event, r, c))
            button.bind("<Button-3>", self.flags)

    def flags(self, event):
        ctk_button = event.widget.master

        if ctk_button.cget("fg_color") == FLAGS_COLOR_BTN:
            ctk_button.configure(fg_color=FG_COLOR_BTN, state="normal") 
        else:
            ctk_button.configure(fg_color=FLAGS_COLOR_BTN, state="disabled")  

    def button_callback(self, event, row, col):
        # first opening test for matrix making
        if not self.first_click_done:
            first_click_pos = (row, col)
            self.matrix = MinesweeperGameLogic.make_matrix(self.column, self.line, self.bomb, first_click_pos)

            self.start_time = time.time()
            self.update_timer()

            self.first_click_done = True
        self.open_cell(event, row, col)

    def update_timer(self):
        if self.game_win or self.game_loss:
            return

        now = time.time()
        self.elapsed_time = now - self.start_time
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        milliseconds = int((self.elapsed_time - int(self.elapsed_time)) * 100)
        
        self.text_time.configure(text=f"{minutes:02}:{seconds:02}:{milliseconds:02}")
        self.after(10, self.update_timer)  # updating the stopwatch update function to 10ms


    def open_cell(self, event, row, col):
        # calls the pressed button

        index = row * self.column + col

        # recording bombs
        for r in range(self.line):      
            for c in range(self.column):
                if self.matrix[r][c] == "*":
                    self.bombs.append((r, c))

        # check for win
        if len(self.opened) + 1 == int((self.total_cell - self.bomb)):
            for (r, c) in self.bombs:
                index_bomb = r * self.column + c
                btn = self.buttons[index_bomb]
                btn.configure(text="*", fg_color=FLAGS_COLOR_BTN, state="disabled")

            self.game_win = True
            self.text_status.configure(text="(^_^)")

        # check if the button is open
        if (row, col) in self.opened:
            return
        self.opened.add((row, col))

        # сheck if an event object was passed
        if event != None:
            # get the button from the widget that triggered the event (without recursion)
            ctk_button = event.widget.master
            if ctk_button.cget("state") == "disabled":
                return
        else:
            # if the event is missing, we get the button by index from the list
            ctk_button = self.buttons[index]
            if ctk_button.cget("state") == "disabled":
                return

        # mine opening check
        if self.matrix[row][col] == "*":
            self.text_status.configure(text="(x_x)")

            # disable all buttons
            for btn in self.buttons:
                btn.configure(state="disabled")

            # show contents of all cells
            for r in range(self.line):
                for c in range(self.column):
                    index = r * self.column + c
                    btn = self.buttons[index]
                    btn.configure(text=self.matrix[r][c])

                    if self.matrix[r][c] == "*":  # if there is a bomb in the cell
                        btn.configure(fg_color=FLAGS_COLOR_BTN, state="disabled")

            self.game_loss = True

            return

        self.buttons[index].configure(text=str(self.matrix[row][col]), state="disabled")

        # if the value is not 0, we expand only it
        if self.matrix[row][col] != 0:
            return

        neighbors = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (-1, 1), (1, -1)]
        for matrix_row, matrix_column in neighbors:
            neighbor_row = row + matrix_row
            neighbor_col = col + matrix_column

            if (0 <= neighbor_row < self.line and 0 <= neighbor_col < self.column):
                self.button_callback(None, neighbor_row, neighbor_col)

    def close_window(self):
        self.destroy()  # close the game window (MinesweeperGameGUI)
        self.main_window.deiconify()  # show the main window (App)