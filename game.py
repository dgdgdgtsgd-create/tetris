import os
import pygame
from objects import Board, PieceBag, create_piece
from effects import Sounds, draw_block
from settings import CELL, COLS, ROWS, BOARD_X, BOARD_Y

WHITE = (240, 243, 250)
MUTED = (165, 174, 195)
BEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "best_score.txt")
DIFFICULTIES = (
    ("Нормальный", 650, 45, 90, "Спокойный старт и плавное ускорение"),
    ("Сложный", 430, 38, 65, "Быстрое падение с первого уровня"),
    ("Хард", 260, 25, 40, "Максимальный темп — думай заранее"),
)


class Game:
    def __init__(self):
        self.font = pygame.font.SysFont("arial", 21)
        self.small_font = pygame.font.SysFont("arial", 16)
        self.big_font = pygame.font.SysFont("arial", 32, bold=True)
        self.best = self.load_best()
        self.sounds = Sounds()
        self.background = None
        self.difficulty_index = 0
        self.restart()

    def load_best(self):
        """Читает лучший результат из файла (если файла нет или он испорчен - 0)."""
        try:
            with open(BEST_FILE, "r", encoding="utf-8") as file:
                return max(0, int(file.read().strip()))
        except (OSError, ValueError):
            return 0

    def save_best(self):
        """Записывает лучший результат в файл."""
        try:
            with open(BEST_FILE, "w", encoding="utf-8") as file:
                file.write(str(self.best))
        except OSError:
            pass

    def check_best(self):
        """Обновляет лучший результат; сохраняет в файл, когда игра закончилась."""
        if self.game_over and not self.end_sound_played:
            self.sounds.play("clear" if self.won else "over")
            self.end_sound_played = True
        if self.score > self.best:
            self.best = self.score
            self.best_changed = True
        if self.game_over and self.best_changed:
            self.save_best()
            self.best_changed = False

    def restart(self):
        self.selecting_difficulty = True
        self.board = Board()
        self.bag = PieceBag()
        self.best_changed = False
        self.current = self.bag.next_piece()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.elapsed_ms = 0
        self.level_elapsed_ms = 0
        self.level_times = []
        self.fall_timer = 0
        self.game_over = False
        self.end_sound_played = False
        self.paused = False
        self.won = False
        self.hold_kind = None
        self.can_hold = True
        self.queue = [self.bag.next_piece() for _ in range(5)]
        self.held_keys = []
        self.repeat_timer = 0
        self.repeat_delay = 180
        self.soft_timer = 0
        self.pieces_placed = 0
        self.rotations = 0
        self.accurate_placements = 0
        self.height_total = 0
        self.longest_combo = 0
        self.combo = -1
        self.notice = ""
        self.notice_timer = 0

    def spawn(self):
        self.current = self.queue.pop(0)
        self.queue.append(self.bag.next_piece())
        self.fall_timer = 0
        self.can_hold = True
        if not self.board.is_valid(self.current):
            self.game_over = True

    def move(self, dx, dy):
        if self.board.is_valid(self.current, dx, dy):
            self.current.x += dx
            self.current.y += dy
            if dx:
                self.sounds.play("move")
            return True
        return False

    def rotate(self):
        rotated = self.current.rotated()
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1), (0, -2)):
            if self.board.is_valid(self.current, dx, dy, shape=rotated):
                self.current.x += dx
                self.current.y += dy
                self.current.shape = rotated
                self.rotations += 1
                self.sounds.play("rotate")
                break

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
        self.fall_timer = 0
        self.sounds.play("hold")

    def lock_piece(self):
        old_holes = self.hole_positions()
        if not self.board.place(self.current):
            self.game_over = True
            return
        self.pieces_placed += 1
        if not (self.hole_positions() - old_holes):
            self.accurate_placements += 1
        cleared = self.board.clear_lines()
        self.height_total += self.stack_height()
        self.sounds.play("clear" if cleared else "lock")
        self.combo = self.combo + 1 if cleared else -1
        self.longest_combo = max(self.longest_combo, self.combo + 1)
        if cleared:
            self.notice = ["", "ЛИНИЯ!", "ДВЕ ЛИНИИ!", "ТРИ ЛИНИИ!", "ТЕТРИС!"][cleared]
            self.notice_timer = 1400
            self.score += max(0, self.combo) * 50 * self.level
        points = [0, 100, 300, 500, 800]
        self.score += points[cleared] * self.level
        self.lines += cleared
        next_level = min(10, self.lines // 10 + 1)
        if next_level != self.level or self.lines >= 100:
            self.level_times.append((self.level, self.level_elapsed_ms))
            self.level_elapsed_ms = 0
        self.level = next_level
        if self.lines >= 100:
            self.game_over = True
            self.won = True
            return
        self.spawn()

    def hole_positions(self):
        """Empty cells below an occupied cell in the same column."""
        holes = set()
        for x in range(COLS):
            covered = False
            for y in range(ROWS):
                if self.board.cells[y][x] is not None:
                    covered = True
                elif covered:
                    holes.add((x, y))
        return holes

    def stack_height(self):
        """Height of the tallest column, sampled after each placement and clear."""
        for y, row in enumerate(self.board.cells):
            if any(cell is not None for cell in row):
                return ROWS - y
        return 0

    def statistics(self):
        count = self.pieces_placed
        return {
            "accuracy": 100 * self.accurate_placements / count if count else 0,
            "rotations": self.rotations,
            "average_height": self.height_total / count if count else 0,
            "longest_combo": self.longest_combo,
        }

    def hard_drop(self):
        while self.move(0, 1):
            self.score += 2
        self.lock_piece()
        self.sounds.play("drop")

    def handle_event(self, event):
        if event.type == pygame.WINDOWFOCUSLOST:
            self.held_keys.clear()
            if not self.game_over:
                self.paused = True
            return
        if event.type == pygame.KEYUP:
            if event.key in self.held_keys:
                self.held_keys.remove(event.key)
                self.repeat_timer = 0
                self.repeat_delay = 180
            return
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_m:
            self.sounds.toggle()
            return

        if self.selecting_difficulty:
            if event.key in (pygame.K_UP, pygame.K_LEFT):
                self.difficulty_index = (self.difficulty_index - 1) % len(DIFFICULTIES)
                self.sounds.play("move")
            elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                self.difficulty_index = (self.difficulty_index + 1) % len(DIFFICULTIES)
                self.sounds.play("move")
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.difficulty_index = event.key - pygame.K_1
                self.sounds.play("move")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.selecting_difficulty = False
                self.paused = False
                self.sounds.play("start")
            return

        if event.key == pygame.K_r:
            self.check_best()
            self.restart()
            return
        if event.key in (pygame.K_p, pygame.K_ESCAPE) and not self.game_over:
            self.paused = not self.paused
            self.sounds.play("pause")
            self.held_keys.clear()
            return
        if self.game_over or self.paused:
            return

        if getattr(event, "repeat", False):
            return
        if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN):
            if event.key in self.held_keys:
                return
            self.held_keys.append(event.key)
            self.repeat_timer = 0
            self.repeat_delay = 180
            self.soft_timer = 0
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
        self.check_best()

    def update(self, dt):
        self.sounds.set_paused(self.paused or self.game_over)
        if self.game_over or self.paused or self.selecting_difficulty:
            return
        self.elapsed_ms += max(0, dt)
        self.level_elapsed_ms += max(0, dt)
        dt = min(dt, 100)
        self.notice_timer = max(0, self.notice_timer - dt)
        horizontal = [key for key in self.held_keys if key in (pygame.K_LEFT, pygame.K_RIGHT)]
        if horizontal:
            self.repeat_timer += dt
            while self.repeat_timer >= self.repeat_delay:
                self.repeat_timer -= self.repeat_delay
                self.repeat_delay = 45
                self.move(-1 if horizontal[-1] == pygame.K_LEFT else 1, 0)
        if pygame.K_DOWN in self.held_keys:
            self.soft_timer += dt
            while self.soft_timer >= 35:
                self.soft_timer -= 35
                if self.move(0, 1):
                    self.score += 1
        self.fall_timer += dt
        speed = self.fall_interval()
        if self.fall_timer >= speed:
            self.fall_timer = 0
            if not self.move(0, 1):
                self.lock_piece()
        self.check_best()

    def fall_interval(self):
        _, initial, increment, minimum, _ = DIFFICULTIES[self.difficulty_index]
        return max(minimum, initial - (self.level - 1) * increment)

    def draw_text(self, screen, text, x, y, font=None, color=WHITE):
        image = (font or self.font).render(text, True, color)
        screen.blit(image, (x, y))

    @staticmethod
    def format_time(milliseconds):
        seconds = int(milliseconds // 1000)
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def draw(self, screen):
        if self.background is None or self.background.get_size() != screen.get_size():
            self.background = pygame.Surface(screen.get_size())
            for y in range(screen.get_height()):
                t = y / screen.get_height()
                pygame.draw.line(self.background, (int(10 + 10*t), int(16 + 5*t), int(31 + 17*t)),
                                 (0, y), (screen.get_width(), y))
            for x in range(0, screen.get_width(), 40):
                pygame.draw.line(self.background, (24, 32, 51), (x, 0), (x, screen.get_height()))
            for y in range(0, screen.get_height(), 40):
                pygame.draw.line(self.background, (24, 32, 51), (0, y), (screen.get_width(), y))
        screen.blit(self.background, (0, 0))
        board_rect = pygame.Rect(BOARD_X, BOARD_Y, COLS * CELL, ROWS * CELL)
        pygame.draw.rect(screen, (17, 48, 62), board_rect.inflate(12, 12), border_radius=10)
        pygame.draw.rect(screen, (60, 166, 185), board_rect.inflate(6, 6), 1, border_radius=5)
        pygame.draw.rect(screen, (11, 17, 29), board_rect)
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
                        draw_block(screen, rect.inflate(-2, -2), self.current.color)

        self.draw_panel(screen, (355, 40, 245, 260))
        self.draw_text(screen, "TETRIS", 373, 48, self.big_font, (98, 233, 235))
        self.draw_text(screen, "NEON BLOCKS", 374, 82, self.small_font, MUTED)
        for label, value, y in (("СЧЁТ", self.score, 100), ("РЕКОРД", self.best, 137),
                                ("ЛИНИИ", self.lines, 174), ("УРОВЕНЬ", self.level, 211)):
            self.draw_text(screen, label, 373, y, self.small_font, MUTED)
            self.draw_text(screen, str(value), 510, y - 3)
        progress = self.lines % 10 / 10
        pygame.draw.rect(screen, (45, 53, 76), (373, 252, 208, 7), border_radius=3)
        if progress:
            pygame.draw.rect(screen, (60, 220, 230), (373, 252, int(208 * progress), 7), border_radius=3)
        self.draw_text(screen, f"Фигур размещено: {self.pieces_placed}", 373, 271, self.small_font, MUTED)

        self.draw_panel(screen, (355, 315, 245, 125))
        self.draw_text(screen, "РЕЗЕРВ  [C]", 373, 325, color=WHITE if self.can_hold else MUTED)
        if self.hold_kind:
            self.draw_preview(screen, create_piece(self.hold_kind), 385, 365, 24)
        else:
            self.draw_text(screen, "C — отложить фигуру", 373, 374, self.small_font, MUTED)

        self.draw_panel(screen, (615, 40, 175, 400))
        self.draw_text(screen, "СЛЕДУЮЩИЕ", 630, 55)
        for index, piece in enumerate(self.queue):
            self.draw_preview(screen, piece, 645, 105 + index * 65, 20)
        self.draw_text(screen, f"Игра: {self.format_time(self.elapsed_ms)}", 630, 401, self.small_font)
        self.draw_text(screen, f"Уровень: {self.format_time(self.level_elapsed_ms)}", 630, 421, self.small_font, MUTED)

        self.draw_panel(screen, (355, 455, 435, 185))
        self.draw_text(screen, "УПРАВЛЕНИЕ", 373, 468)
        for index, text in enumerate(("← / →   Движение (можно удерживать)",
                                      "↓   Ускорить     ↑   Повернуть",
                                      "Пробел   Мгновенно опустить",
                                      "C   Резерв     P / Esc   Пауза",
                                      "R   Заново     M   Звук")):
            self.draw_text(screen, text, 373, 504 + index * 24, self.small_font, MUTED)
        audio_label = "ЗВУК ВЫКЛ" if self.sounds.muted else "ЗВУК ВКЛ" if self.sounds.clips else "ЗВУК НЕДОСТУПЕН"
        self.draw_text(screen, audio_label, 620, 650, self.small_font, MUTED)
        self.draw_text(screen, DIFFICULTIES[self.difficulty_index][0], 355, 650, self.small_font, (98, 233, 235))
        if self.notice_timer > 0:
            self.draw_text(screen, self.notice, BOARD_X + 25, 8, self.font, (60, 220, 230))
        if self.paused or self.game_over:
            overlay = pygame.Surface((COLS * CELL, ROWS * CELL), pygame.SRCALPHA)
            overlay.fill((10, 14, 25, 215))
            screen.blit(overlay, (BOARD_X, BOARD_Y))
            message = "ПОБЕДА!" if self.won else "ИГРА ОКОНЧЕНА" if self.game_over else "ПАУЗА"
            image = self.big_font.render(message, True, WHITE)
            screen.blit(image, (BOARD_X + (COLS * CELL - image.get_width()) // 2, 285))
            self.draw_text(screen, "R — заново" if self.game_over else "P / Esc — продолжить", BOARD_X + 35, 340, self.font)
        if self.game_over:
            self.draw_statistics(screen)
        if self.selecting_difficulty:
            self.draw_difficulty_menu(screen)

    def draw_difficulty_menu(self, screen):
        shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shade.fill((5, 9, 18, 235))
        screen.blit(shade, (0, 0))
        self.draw_panel(screen, (120, 100, 580, 480))
        self.draw_text(screen, "ВЫБЕРИ СЛОЖНОСТЬ", 155, 125, self.big_font, (98, 233, 235))
        for index, (name, initial, _, _, description) in enumerate(DIFFICULTIES):
            rect = pygame.Rect(150, 190 + index * 100, 520, 88)
            selected = index == self.difficulty_index
            pygame.draw.rect(screen, (31, 60, 76) if selected else (20, 26, 42), rect, border_radius=9)
            if selected:
                pygame.draw.rect(screen, (98, 233, 235), rect, 2, border_radius=9)
            self.draw_text(screen, f"{index + 1}   {name}", 169, rect.y + 10,
                           color=(98, 233, 235) if selected else WHITE)
            self.draw_text(screen, description, 169, rect.y + 42, self.small_font, MUTED)
            self.draw_text(screen, f"Старт: {initial / 1000:.2f} сек. на клетку", 169, rect.y + 63, self.small_font, MUTED)
        self.draw_text(screen, "↑ / ↓ или 1–3 — выбрать   •   Enter — играть", 155, 515, self.font)
        self.draw_text(screen, "R во время игры — новая партия и выбор сложности", 155, 550, self.small_font, MUTED)

    def draw_statistics(self, screen):
        shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shade.fill((5, 9, 18, 225))
        screen.blit(shade, (0, 0))
        self.draw_panel(screen, (140, 38, 540, 607))
        title = "ПОБЕДА!" if self.won else "ИТОГИ ИГРЫ"
        self.draw_text(screen, title, 175, 54, self.big_font, (98, 233, 235))
        self.draw_text(screen, f"Счёт: {self.score}   •   Линий: {self.lines}", 175, 99)
        self.draw_text(screen, DIFFICULTIES[self.difficulty_index][0], 500, 65, self.small_font, MUTED)
        stats = self.statistics()
        rows = (
            ("Точность размещения", f"{stats['accuracy']:.1f}%"),
            ("Число вращений", str(stats['rotations'])),
            ("Средняя высота стопки", f"{stats['average_height']:.1f} клеток"),
            ("Самое длинное комбо", str(stats['longest_combo'])),
            ("Фигур размещено", str(self.pieces_placed)),
            ("Время игры (без пауз)", self.format_time(self.elapsed_ms)),
        )
        for index, (label, value) in enumerate(rows):
            y = 145 + index * 34
            self.draw_text(screen, label, 175, y, color=MUTED)
            rendered = self.font.render(value, True, WHITE)
            screen.blit(rendered, (645 - rendered.get_width(), y))
        self.draw_text(screen, "ВРЕМЯ ПО УРОВНЯМ", 175, 357, self.small_font, (98, 233, 235))
        times = list(self.level_times)
        if not self.won:
            times.append((self.level, self.level_elapsed_ms))
        for index, (level, duration) in enumerate(times):
            column, row = divmod(index, 5)
            suffix = " (не завершён)" if not self.won and index == len(times) - 1 else ""
            self.draw_text(screen, f"{level}: {self.format_time(duration)}{suffix}",
                           175 + column * 240, 385 + row * 24, self.small_font, MUTED)
        self.draw_text(screen, "Точность: фигуры без новых пустот под блоками.", 175, 516, self.small_font, MUTED)
        self.draw_text(screen, "Высота: средняя по ходам после удаления линий.", 175, 541, self.small_font, MUTED)
        self.draw_text(screen, "Комбо: ходы с очисткой линий подряд.", 175, 566, self.small_font, MUTED)
        self.draw_text(screen, "R — сыграть ещё раз", 175, 603, color=(98, 233, 235))

    def draw_panel(self, screen, rect):
        shadow = pygame.Rect(rect).move(0, 5)
        pygame.draw.rect(screen, (7, 11, 22), shadow, border_radius=12)
        pygame.draw.rect(screen, (25, 31, 48), rect, border_radius=12)
        pygame.draw.rect(screen, (47, 58, 82), rect, width=1, border_radius=12)
        accent = pygame.Rect(rect)
        pygame.draw.line(screen, (66, 142, 164), (accent.x + 18, accent.y), (accent.x + 62, accent.y), 2)

    def draw_preview(self, screen, piece, x, y, size):
        for row_index, row in enumerate(piece.shape):
            for col_index, value in enumerate(row):
                if value:
                    rect = pygame.Rect(x + col_index * size, y + row_index * size, size - 2, size - 2)
                    draw_block(screen, rect, piece.color)
