import random
import tkinter as tk

W, H, S = 10, 20, 30  # ширина, высота стакана (в клетках) и размер клетки (в пикселях)

SHAPES = {
    "I": [(-1, 0), (0, 0), (1, 0), (2, 0)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(-1, 0), (0, 0), (1, 0), (0, 1)],
    "S": [(0, 0), (1, 0), (-1, 1), (0, 1)],
    "Z": [(-1, 0), (0, 0), (0, 1), (1, 1)],
    "J": [(-1, 0), (0, 0), (1, 0), (-1, 1)],
    "L": [(-1, 0), (0, 0), (1, 0), (1, 1)],
}

COLORS = {
    "I": "#3ec1d3", "O": "#f2c94c", "T": "#a66cff", "S": "#4cc38a",
    "Z": "#ef5b5b", "J": "#4f7cff", "L": "#ff7a3d",
}

LINE_POINTS = [0, 100, 300, 500, 800]


class Tetris:
    def __init__(self, root):
        self.root = root
        root.title("Тетрис")
        root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=W * S + 170, height=H * S,
                                bg="#15182b", highlightthickness=0)
        self.canvas.pack()
        root.bind("<Key>", self.on_key)
        self.job = None
        self.new_game()

    # ---------- состояние игры ----------
    def new_game(self):
        if self.job:
            self.root.after_cancel(self.job)
        self.board = [[None] * W for _ in range(H)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.over = False
        self.paused = False
        self.next_name = random.choice(list(SHAPES))
        self.spawn()
        self.tick()

    def spawn(self):
        self.name = self.next_name
        self.next_name = random.choice(list(SHAPES))
        self.cells = list(SHAPES[self.name])
        self.x, self.y = W // 2 - 1, 0
        if not self.fits(self.cells, self.x, self.y):
            self.over = True

    # ---------- цикл игры ----------
    def tick(self):
        if not self.over and not self.paused:
            if not self.move(0, 1):
                self.lock()
        self.draw()
        delay = max(80, 600 - (self.level - 1) * 50)
        self.job = self.root.after(delay, self.tick)


if __name__ == "__main__":
    root = tk.Tk()
    Tetris(root)
    root.mainloop()
