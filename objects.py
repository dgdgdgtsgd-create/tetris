import random
import pygame
from settings import CELL, COLS, ROWS, BOARD_X, BOARD_Y, COLORS, SHAPES


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


class Board:
    def __init__(self):
        self.cells = [[None for _ in range(COLS)] for _ in range(ROWS)]

    def is_valid(self, piece, dx=0, dy=0, shape=None):
        shape = shape or piece.shape
        for row_index, row in enumerate(shape):
            for col_index, value in enumerate(row):
                if not value:
                    continue
                x = piece.x + col_index + dx
                y = piece.y + row_index + dy
                if x < 0 or x >= COLS or y >= ROWS:
                    return False
                if y >= 0 and self.cells[y][x] is not None:
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
        return True

    def clear_lines(self):
        remaining = [row for row in self.cells if any(cell is None for cell in row)]
        cleared = ROWS - len(remaining)
        self.cells = [[None for _ in range(COLS)] for _ in range(cleared)] + remaining
        return cleared

    def draw(self, screen):
        for y in range(ROWS):
            for x in range(COLS):
                rect = pygame.Rect(BOARD_X + x * CELL, BOARD_Y + y * CELL, CELL, CELL)
                color = self.cells[y][x]
                if color is not None:
                    pygame.draw.rect(screen, color, rect.inflate(-2, -2), border_radius=4)
                pygame.draw.rect(screen, (48, 54, 72), rect, 1)
