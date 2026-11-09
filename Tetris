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

    def fits(self, cells, x, y):
        for dx, dy in cells:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= W or ny >= H:
                return False
            if ny >= 0 and self.board[ny][nx]:
                return False
        return True

    def move(self, dx, dy):
        if self.fits(self.cells, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def rotate(self):
        if self.name == "O":
            return
        new = [(-dy, dx) for dx, dy in self.cells]
        for kick in (0, -1, 1, -2, 2):  # пробуем сдвинуть фигуру от стенки
            if self.fits(new, self.x + kick, self.y):
                self.cells = new
                self.x += kick
                return

    def lock(self):
        for dx, dy in self.cells:
            if self.y + dy >= 0:
                self.board[self.y + dy][self.x + dx] = self.name
        self.clear_lines()
        self.spawn()

    def clear_lines(self):
        kept = [row for row in self.board if not all(row)]
        cleared = H - len(kept)
        self.board = [[None] * W for _ in range(cleared)] + kept
        if cleared:
            self.score += LINE_POINTS[cleared] * self.level
            self.lines += cleared
            self.level = self.lines // 10 + 1

    def hard_drop(self):
        while self.move(0, 1):
            self.score += 2
        self.lock()

    # ---------- цикл игры ----------
    def tick(self):
        if not self.over and not self.paused:
            if not self.move(0, 1):
                self.lock()
        self.draw()
        delay = max(80, 600 - (self.level - 1) * 50)
        self.job = self.root.after(delay, self.tick)

    def on_key(self, event):
        key = event.keysym
        low = key.lower()  # "r"/"p" и русские "к"/"з" на той же клавише
        if low in ("r", "cyrillic_ka"):
            self.new_game()
            return
        if low in ("p", "cyrillic_ze") and not self.over:
            self.paused = not self.paused
        if self.over or self.paused:
            self.draw()
            return
        if key == "Left":
            self.move(-1, 0)
        elif key == "Right":
            self.move(1, 0)
        elif key == "Down":
            if self.move(0, 1):
                self.score += 1
        elif key == "Up":
            self.rotate()
        elif key == "space":
            self.hard_drop()
        self.draw()

    # ---------- рисование ----------
    def cell(self, x, y, name, ox=0, oy=0):
        self.canvas.create_rectangle(
            ox + x * S + 1, oy + y * S + 1,
            ox + (x + 1) * S - 1, oy + (y + 1) * S - 1,
            fill=COLORS[name], outline="")

    def draw(self):
        c = self.canvas
        c.delete("all")
        for y in range(H):
            for x in range(W):
                if self.board[y][x]:
                    self.cell(x, y, self.board[y][x])
                else:
                    c.create_rectangle(x * S, y * S, (x + 1) * S, (y + 1) * S,
                                       outline="#22264a")
        if not self.over:
            for dx, dy in self.cells:
                if self.y + dy >= 0:
                    self.cell(self.x + dx, self.y + dy, self.name)

        px = W * S + 20
        text = dict(fill="#f4f1ea", anchor="nw", font=("Arial", 14))
        c.create_text(px, 20, text=f"Очки: {self.score}", **text)
        c.create_text(px, 50, text=f"Линии: {self.lines}", **text)
        c.create_text(px, 80, text=f"Уровень: {self.level}", **text)
        c.create_text(px, 130, text="Следующая:", **text)
        for dx, dy in SHAPES[self.next_name]:
            self.cell(dx + 1, dy + 1, self.next_name, ox=px, oy=150)
        c.create_text(px, 330, anchor="nw", fill="#b9bdd6", font=("Arial", 11),
                      text="← →  двигать\n↑  повернуть\n↓  быстрее\nПробел  сбросить\nP  пауза\nR  заново")

        if self.over:
            c.create_text(W * S // 2, H * S // 2, text="Игра окончена\nR — заново",
                          fill="#ff7a3d", font=("Arial", 22, "bold"), justify="center")
        elif self.paused:
            c.create_text(W * S // 2, H * S // 2, text="Пауза",
                          fill="#f2c94c", font=("Arial", 26, "bold"))


if __name__ == "__main__":
    root = tk.Tk()
    Tetris(root)
    root.mainloop()
