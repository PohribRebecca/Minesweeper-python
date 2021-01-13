# Python Version 2.7.3
# File: minesweeper.py

from tkinter import *
from tkinter import messagebox as tkMessageBox
from collections import deque
import random
import platform
import time
from datetime import time, date, datetime
import time

SIZE_X = 50
SIZE_Y = 20

STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"

window = None
settings = None


class Settings():
    def __init__(self, tk):
        '''self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()'''
        self.tk = tk
        tk.geometry('500x500')

        # set up labels/UI
        self.labels = {
            "time": Label(self.tk, text="time"),
            "mines": Label(self.tk, text="Mines"),
            "grid": Label(self.tk, text="Grid Dimension")
        }

        self.entries = {
            "mineEntry": Entry(self.tk),
            "timeEntry": Entry(self.tk),
            "gridEntry": Entry(self.tk)
        }
        self.button = {
            "Start Game": Button(self.tk, text='Start Game', command=self.startGame)
        }

        self.labels["time"].grid(row=0, column=0, columnspan=SIZE_Y)  # top full width
        self.labels["mines"].grid(row=SIZE_X + 1, column=0, columnspan=int(SIZE_Y / 2))  # bottom left
        self.labels["grid"].grid(row=SIZE_X + 1, column=int(SIZE_Y / 2) - 1, columnspan=int(SIZE_Y / 2))  # bottom right

        self.labels["time"].pack()
        self.labels["time"].place(x=5, y=25)

        self.entries["mineEntry"].grid(row=int(SIZE_X / 2), column=0, columnspan=int(SIZE_Y / 2), padx=3, pady=3)
        self.entries["timeEntry"].grid(row=0, column=0, columnspan=SIZE_Y, padx=3, pady=3)
        self.entries["gridEntry"].grid(row=SIZE_X + 1, column=int(SIZE_Y / 2) - 1, columnspan=int(SIZE_Y / 2), padx=3,
                                       pady=3)
        self.button["Start Game"].grid(row=SIZE_X, column=int(SIZE_Y / 2) - 1, columnspan=int(SIZE_Y / 2), padx=3,
                                       pady=3)

    def startGame(self):
        self.start = 1
        gridSize = self.entries["gridEntry"].get()
        mines = self.entries["mineEntry"].get()
        time = self.entries["timeEntry"].get()
        mines = int(mines) + 1
        time = int(time)
        gridSize = int(gridSize)
        if mines > 0 and time > 0 and gridSize > 0:
            game = Minesweeper(window, mines, time, gridSize)

        else:
            res = tkMessageBox.askyesno("Error", "The data you have introduced is not valid!")
            self.tk.quit()


class Minesweeper:

    def __init__(self, tk, mines, time, gridSize):
        self.mines = mines
        self.startTime = time
        self.gridSize = gridSize
        # import images
        self.images = {
            "plain": PhotoImage(file="images/tile_plain.gif"),
            "clicked": PhotoImage(file="images/tile_clicked.gif"),
            "mine": PhotoImage(file="images/tile_mine.gif"),
            "flag": PhotoImage(file="images/tile_flag.gif"),
            "wrong": PhotoImage(file="images/tile_wrong.gif"),
            "numbers": []
        }
        for i in range(1, 9):
            self.images["numbers"].append(PhotoImage(file="images/tile_" + str(i) + ".gif"))

        # set up frame
        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()

        # set up labels/UI
        self.labels = {
            "time": Label(self.frame, text="00:00:00"),
            "mines": Label(self.frame, text="Mines: 0"),
            "flags": Label(self.frame, text="Flags: 0")
        }
        self.labels["time"].grid(row=0, column=0, columnspan=self.gridSize)  # top full width
        self.labels["mines"].grid(row=SIZE_X + 1, column=0, columnspan=int(self.gridSize / 2))  # bottom left
        self.labels["flags"].grid(row=SIZE_X + 1, column=int(self.gridSize / 2) - 1,
                                  columnspan=int(self.gridSize / 2))  # bottom right

        self.restart()  # start game
        self.updateTimer2()  # init timer

    def setup(self):
        # create flag and clicked tile variables
        self.flagCount = 0
        self.correctFlagCount = 0
        self.clickedCount = 0

        # create buttons
        self.tiles = dict({})
        for x in range(0, self.gridSize):
            for y in range(0, self.gridSize):
                if y == 0:
                    self.tiles[x] = {}

                id = str(x) + "_" + str(y)
                isMine = False

                # tile image changeable for debug reasons:
                gfx = self.images["plain"]

                # currently random amount of mines
                if random.uniform(0.0, 1.0) < 0.1:
                    isMine = True
                    '''self.mines += 1'''

                tile = {
                    "id": id,
                    "isMine": isMine,
                    "state": STATE_DEFAULT,
                    "coords": {
                        "x": x,
                        "y": y
                    },
                    "button": Button(self.frame, image=gfx),
                    "mines": 0  # calculated after grid is built
                }

                tile["button"].bind(BTN_CLICK, self.onClickWrapper(x, y))
                tile["button"].bind(BTN_FLAG, self.onRightClickWrapper(x, y))
                tile["button"].grid(row=x + 1, column=y)  # offset by 1 row for timer

                self.tiles[x][y] = tile

        # loop again to find nearby mines and display number on tile
        for x in range(0, self.gridSize):
            for y in range(0, self.gridSize):
                mc = 0
                for n in self.getNeighbors(x, y):
                    mc += 1 if n["isMine"] else 0
                self.tiles[x][y]["mines"] = mc

    def restart(self):
        self.setup()
        self.refreshLabels()

    def refreshLabels(self):
        self.labels["flags"].config(text="Flags: " + str(self.flagCount))
        self.labels["mines"].config(text="Mines: " + str(self.mines))

    def updateTimer2(self):
        mins, secs = divmod(self.startTime, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        if self.startTime > 0:
            self.startTime = self.startTime - 1
            time.sleep(1)
            self.labels["time"].config(text=timer)
        else:
            self.labels["time"].config(text="time is up")
        self.frame.after(100, self.updateTimer2)

    def getNeighbors(self, x, y):
        neighbors = []
        coords = [
            {"x": x - 1, "y": y - 1},  # top right
            {"x": x - 1, "y": y},  # top middle
            {"x": x - 1, "y": y + 1},  # top left
            {"x": x, "y": y - 1},  # left
            {"x": x, "y": y + 1},  # right
            {"x": x + 1, "y": y - 1},  # bottom right
            {"x": x + 1, "y": y},  # bottom middle
            {"x": x + 1, "y": y + 1},  # bottom left
        ]
        for n in coords:
            try:
                neighbors.append(self.tiles[n["x"]][n["y"]])
            except KeyError:
                pass
        return neighbors

    def gameOver(self, won):
        for x in range(0, self.gridSize):
            for y in range(0, self.gridSize):
                if self.tiles[x][y]["isMine"] == False and self.tiles[x][y]["state"] == STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(image=self.images["wrong"])
                if self.tiles[x][y]["isMine"] == True and self.tiles[x][y]["state"] != STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(image=self.images["mine"])

        self.tk.update()

        msg = "You Win! Play again?" if won else "You Lose! Play again?"
        res = tkMessageBox.askyesno("Game Over", msg)
        if res:
            self.restart()
        else:
            self.tk.quit()

    def onClickWrapper(self, x, y):
        return lambda Button: self.onClick(self.tiles[x][y])

    def onRightClickWrapper(self, x, y):
        return lambda Button: self.onRightClick(self.tiles[x][y])

    def onClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        if tile["isMine"] == True:
            # end game
            self.gameOver(False)
            return

        # change image
        if tile["mines"] == 0:
            tile["button"].config(image=self.images["clicked"])
            self.clearSurroundingTiles(tile["id"])
        else:
            tile["button"].config(image=self.images["numbers"][tile["mines"] - 1])
        # if not already set as clicked, change state and count
        if tile["state"] != STATE_CLICKED:
            tile["state"] = STATE_CLICKED
            self.clickedCount += 1
        if self.clickedCount == (self.gridSize * self.gridSize) - self.mines:
            self.gameOver(True)

    def onRightClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        # if not clicked
        if tile["state"] == STATE_DEFAULT:
            tile["button"].config(image=self.images["flag"])
            tile["state"] = STATE_FLAGGED
            tile["button"].unbind(BTN_CLICK)
            # if a mine
            if tile["isMine"] == True:
                self.correctFlagCount += 1
            self.flagCount += 1
            self.refreshLabels()
        # if flagged, unflag
        elif tile["state"] == 2:
            tile["button"].config(image=self.images["plain"])
            tile["state"] = 0
            tile["button"].bind(BTN_CLICK, self.onClickWrapper(tile["coords"]["x"], tile["coords"]["y"]))
            # if a mine
            if tile["isMine"] == True:
                self.correctFlagCount -= 1
            self.flagCount -= 1
            self.refreshLabels()

    def clearSurroundingTiles(self, id):
        queue = deque([id])

        while len(queue) != 0:
            key = queue.popleft()
            parts = key.split("_")
            x = int(parts[0])
            y = int(parts[1])

            for tile in self.getNeighbors(x, y):
                self.clearTile(tile, queue)

    def clearTile(self, tile, queue):
        if tile["state"] != STATE_DEFAULT:
            return

        if tile["mines"] == 0:
            tile["button"].config(image=self.images["clicked"])
            queue.append(tile["id"])
        else:
            tile["button"].config(image=self.images["numbers"][tile["mines"] - 1])

        tile["state"] = STATE_CLICKED
        self.clickedCount += 1


### END OF CLASSES ###

def main():
    # create Tk instance
    window = Tk()
    settings = Tk()
    # set program title
    window.title("Minesweeper")
    # create game instance
    # minesweeper = Minesweeper(window)
    sets = Settings(settings)
    # run event loop
    window.mainloop()


if __name__ == "__main__":
    main()
