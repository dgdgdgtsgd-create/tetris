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
