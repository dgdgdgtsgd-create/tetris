import pygame
from objects import Board, create_piece
from settings import CELL, COLS, ROWS, BOARD_X, BOARD_Y

WHITE = (240, 243, 250)
MUTED = (165, 174, 195)


class Game:
    def __init__(self):
        self.font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 48)
        self.restart()

    def restart(self):
        self.board = Board()
        self.current = create_piece()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.fall_timer = 0
        self.game_over = False
        self.paused = False
        self.won = False
        self.hold_kind = None
        self.can_hold = True
        self.spawn_next = create_piece()

    def spawn(self):
        self.current = self.spawn_next
        self.spawn_next = create_piece()
        self.can_hold = True
        if not self.board.is_valid(self.current):
            self.game_over = True

    def move(self, dx, dy):
        if self.board.is_valid(self.current, dx, dy):
            self.current.x += dx
            self.current.y += dy
            return True
        return False

    def rotate(self):
        rotated = self.current.rotated()
        if self.board.is_valid(self.current, shape=rotated):
            self.current.shape = rotated

    def ghost_y(self):
        """Функция 4: на какой строке фигура приземлится (проекция)."""
        dy = 0
        while self.board.is_valid(self.current, 0, dy + 1):
            dy += 1
        return self.current.y + dy

    def hold(self):
        """Функция 5: отложить текущую фигуру (клавиша C), раз за ход."""
        if not self.can_hold:
            return
        kind = self.current.kind
        if self.hold_kind is None:
            self.hold_kind = kind
            self.spawn()
        else:
            self.current = create_piece(self.hold_kind)
            self.hold_kind = kind
            if not self.board.is_valid(self.current):
                self.game_over = True
        self.can_hold = False

    def lock_piece(self):
        if not self.board.place(self.current):
            self.game_over = True
            return
        cleared = self.board.clear_lines()
        points = [0, 100, 300, 500, 800]
        self.score += points[cleared] * self.level
        self.lines += cleared
        self.level = self.lines // 10 + 1
        if self.lines >= 100:
            self.game_over = True
            self.won = True
            return
        self.spawn()

    def hard_drop(self):
        while self.move(0, 1):
            self.score += 2
        self.lock_piece()

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_r:
            self.restart()
            return
        if event.key == pygame.K_p and not self.game_over:
            self.paused = not self.paused
            return
        if self.game_over or self.paused:
            return

        if event.key == pygame.K_LEFT:
            self.move(-1, 0)
        elif event.key == pygame.K_RIGHT:
            self.move(1, 0)
        elif event.key == pygame.K_DOWN:
            if self.move(0, 1):
                self.score += 1
        elif event.key == pygame.K_UP:
            self.rotate()
        elif event.key == pygame.K_SPACE:
            self.hard_drop()
        elif event.key == pygame.K_c:
            self.hold()

    def update(self, dt):
        if self.game_over or self.paused:
            return
        self.fall_timer += dt
        speed = max(90, 650 - (self.level - 1) * 45)
        if self.fall_timer >= speed:
            self.fall_timer = 0
            if not self.move(0, 1):
                self.lock_piece()

    def draw_text(self, screen, text, x, y, font=None, color=WHITE):
        image = (font or self.font).render(text, True, color)
        screen.blit(image, (x, y))

    def draw(self, screen):
        self.board.draw(screen)
        if not self.game_over:
            ghost_y = self.ghost_y()
            for row_index, row in enumerate(self.current.shape):
                for col_index, value in enumerate(row):
                    if value:
                        ghost = pygame.Rect(
                            BOARD_X + (self.current.x + col_index) * CELL,
                            BOARD_Y + (ghost_y + row_index) * CELL,
                            CELL, CELL
                        )
                        pygame.draw.rect(screen, self.current.color,
                                         ghost.inflate(-2, -2), 2, border_radius=4)
            for row_index, row in enumerate(self.current.shape):
                for col_index, value in enumerate(row):
                    if value:
                        rect = pygame.Rect(
                            BOARD_X + (self.current.x + col_index) * CELL,
                            BOARD_Y + (self.current.y + row_index) * CELL,
                            CELL, CELL
                        )
                        pygame.draw.rect(screen, self.current.color,
                                         rect.inflate(-2, -2), border_radius=4)

        panel_x = 355
        self.draw_text(screen, "TETRIS", panel_x, 55, self.big_font)
        self.draw_text(screen, f"Score: {self.score}", panel_x, 130)
        self.draw_text(screen, f"Lines: {self.lines}", panel_x, 175)
        self.draw_text(screen, f"Level: {self.level}", panel_x, 220)
        hold_text = self.hold_kind if self.hold_kind else "-"
        self.draw_text(screen, f"Hold: {hold_text}", panel_x, 265)
        self.draw_text(screen, "Controls:", panel_x, 310)
        self.draw_text(screen, "Arrows - move", panel_x, 350, color=MUTED)
        self.draw_text(screen, "Up - rotate", panel_x, 385, color=MUTED)
        self.draw_text(screen, "Space - drop", panel_x, 420, color=MUTED)
        self.draw_text(screen, "C - hold", panel_x, 455, color=MUTED)
        self.draw_text(screen, "P - pause", panel_x, 490, color=MUTED)
        self.draw_text(screen, "R - restart", panel_x, 525, color=MUTED)

        if self.paused:
            self.draw_text(screen, "PAUSED", 205, 300, self.big_font)
        if self.game_over:
            message = "YOU WIN!" if self.won else "GAME OVER"
            self.draw_text(screen, message, 175, 300, self.big_font)
            self.draw_text(screen, "Press R to restart", 165, 350)
