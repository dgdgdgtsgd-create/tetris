# модуль деңгейі (класстан тыс)
SHAPES = {
    "I": [(-1, 0), (0, 0), (1, 0), (2, 0)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(-1, 0), (0, 0), (1, 0), (0, 1)],
    "S": [(0, 0), (1, 0), (-1, 1), (0, 1)],
    "Z": [(-1, 0), (0, 0), (0, 1), (1, 1)],
    "J": [(-1, 0), (0, 0), (1, 0), (-1, 1)],
    "L": [(-1, 0), (0, 0), (1, 0), (1, 1)],
}

# класс ішіндегі әдістер
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

    def hard_drop(self):
        while self.move(0, 1):
            self.score += 2
        self.lock()
