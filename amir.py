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