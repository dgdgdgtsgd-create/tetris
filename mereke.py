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
