import random
import tkinter as tk

W, H, S = 10, 20, 30  # ширина, высота стакана (в клетках) и размер клетки (в пикселях)


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
