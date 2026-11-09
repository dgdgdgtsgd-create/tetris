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
