# модуль деңгейі (класстан тыс)
LINE_POINTS = [0, 100, 300, 500, 800]

# класс ішіндегі әдістер
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
