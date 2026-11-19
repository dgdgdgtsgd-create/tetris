import random
import pygame
from effects import draw_block
from settings import CELL, COLS, ROWS, BOARD_X, BOARD_Y, COLORS, SHAPES


_IMAGE_CACHE = {}


def block_image(color):
    """Картинка одной клетки (кешируется, чтобы не рисовать её заново для каждого спрайта)."""
    if color not in _IMAGE_CACHE:
        image = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        draw_block(image, pygame.Rect(1, 1, CELL - 2, CELL - 2), color)
        _IMAGE_CACHE[color] = image
    return _IMAGE_CACHE[color]


class Block(pygame.sprite.Sprite):
    """Родительский спрайт: одна клетка поля. rect лежит в экранных координатах."""

    def __init__(self, col, row, color):
        super().__init__()
        self.col = col
        self.row = row
        self.color = color
        self.image = block_image(color)
        self.rect = self.image.get_rect(topleft=(BOARD_X + col * CELL, BOARD_Y + row * CELL))


class LockedBlock(Block):
    """Клетка, которая уже легла в стопку."""


class PieceBlock(Block):
    """Клетка падающей фигуры (и её проекции для проверки столкновений)."""


class Piece:
    def __init__(self, kind):
        self.kind = kind
        self.color = COLORS[kind]
        self.shape = self.get_shape()
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def get_shape(self):
        return [row[:] for row in SHAPES[self.kind]]

    def rotated(self):
        """Возвращает форму после поворота (не меняя саму фигуру)."""
        return [list(row) for row in zip(*self.shape[::-1])]

    def rotate(self):
        self.shape = self.rotated()

    def make_blocks(self, dx=0, dy=0, shape=None):
        """Группа спрайтов-клеток фигуры, сдвинутая на (dx, dy)."""
        group = pygame.sprite.Group()
        for row_index, row in enumerate(shape or self.shape):
            for col_index, value in enumerate(row):
                if value:
                    group.add(PieceBlock(self.x + col_index + dx,
                                         self.y + row_index + dy, self.color))
        return group


class IPiece(Piece):
    def __init__(self):
        super().__init__("I")


class OPiece(Piece):
    def __init__(self):
        super().__init__("O")

    def rotated(self):
        # Квадрат при повороте не меняется - переопределяем метод родителя
        return [row[:] for row in self.shape]


class TPiece(Piece):
    def __init__(self):
        super().__init__("T")


class JPiece(Piece):
    def __init__(self):
        super().__init__("J")


class LPiece(Piece):
    def __init__(self):
        super().__init__("L")


class SPiece(Piece):
    def __init__(self):
        super().__init__("S")


class ZPiece(Piece):
    def __init__(self):
        super().__init__("Z")


PIECE_CLASSES = {
    "I": IPiece, "O": OPiece, "T": TPiece, "J": JPiece,
    "L": LPiece, "S": SPiece, "Z": ZPiece,
}


def create_piece(kind=None):
    if kind is None:
        kind = random.choice(list(PIECE_CLASSES))
    return PIECE_CLASSES[kind]()


class PieceBag:
    """Мешок из 7 фигур: каждая фигура выпадает по одному разу, потом мешок перемешивается заново."""

    def __init__(self):
        self.kinds = []

    def refill(self):
        self.kinds = list(PIECE_CLASSES)
        random.shuffle(self.kinds)

    def next_piece(self):
        if not self.kinds:
            self.refill()
        return create_piece(self.kinds.pop())


class Board:
    def __init__(self):
        self.cells = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.blocks = pygame.sprite.Group()  # все лежащие клетки (LockedBlock)

    def is_valid(self, piece, dx=0, dy=0, shape=None):
        for block in piece.make_blocks(dx, dy, shape):
            if block.col < 0 or block.col >= COLS or block.row >= ROWS:
                return False
            # Столкновение с лежащими клетками проверяем через spritecollideany
            if pygame.sprite.spritecollideany(block, self.blocks):
                return False
        return True

    def place(self, piece):
        for row_index, row in enumerate(piece.shape):
            for col_index, value in enumerate(row):
                if value:
                    x = piece.x + col_index
                    y = piece.y + row_index
                    if y < 0:
                        return False
                    self.cells[y][x] = piece.color
                    self.blocks.add(LockedBlock(x, y, piece.color))
        return True

    def clear_lines(self):
        remaining = [row for row in self.cells if any(cell is None for cell in row)]
        cleared = ROWS - len(remaining)
        self.cells = [[None for _ in range(COLS)] for _ in range(cleared)] + remaining
        if cleared:
            self.rebuild_blocks()
        return cleared

    def rebuild_blocks(self):
        """Пересоздаёт группу спрайтов по сетке после удаления линий."""
        self.blocks.empty()
        for y in range(ROWS):
            for x in range(COLS):
                if self.cells[y][x] is not None:
                    self.blocks.add(LockedBlock(x, y, self.cells[y][x]))

    def draw(self, screen):
        for y in range(ROWS):
            for x in range(COLS):
                rect = pygame.Rect(BOARD_X + x * CELL, BOARD_Y + y * CELL, CELL, CELL)
                pygame.draw.rect(screen, (26, 36, 54), rect, 1)
        self.blocks.draw(screen)
