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
