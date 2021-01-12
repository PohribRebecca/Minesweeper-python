from tkinter import *
from tkinter import messagebox as tkMessageBox, ttk
from collections import deque
import tkinter as tk
import random
import platform
from datetime import time, date, datetime

''' 
vom face cate o clasa pentru fiecare tip de joc
'''


class minesweeperHard:
    def __init__(self, tk):
        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()

        self.images = {
            "plain": PhotoImage(file="images/tile_plain.gif"),
            "click": PhotoImage(file="images/tile_clicked.gif"),
            "mine": PhotoImage(file="images/tile_mine.gif"),
            "flag": PhotoImage(file="images/tile_flag.gif"),
            "wrong": PhotoImage(file="images/tile_wrong.gif"),
            "numbers": []
        }


def initialize():
    x = 10
    print(x)


def main():
    window = Tk()
    window.title("Minesweeper-configurari")
    grid = Label(window, text="Choose the grid dimension")
    grid.place(x=2, y=2)

    mineLabel = Label(window, text="Choose the number of mines")
    btn1 = Button(window, text='5', command=initialize)
    btn1.place(x=5, y=25)
    btn2 = Button(window, text='10', command=initialize)
    btn2.place(x=85, y=25)
    btn3 = Button(window, text='15', command=initialize)
    btn3.place(x=165, y=25)

    minesweeper = minesweeperHard(window)
    window.geometry("200x200")
    window.mainloop()


if __name__ == "__main__":
    main()
