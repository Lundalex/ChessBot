import chess
import math


class AbdadaBoard(chess.Board):
    def genmoves(self):
        return list(self.legal_moves)

    def move(self, move):
        super().push(move)

    def outcome(self):
        if self.is_checkmate():
            return -1
        elif self.is_stalemate() or self.is_insufficient_material():
            return 0
        else:
            return 3

    def move_san(self, san):
        move = chess.Move.from_uci(self.san2uci(san))
        super().push(move)

    def unmove(self):
        super().pop()

    def string(self):
        return super().__str__() + str(self.turn == chess.WHITE)

    def print_board(self):
        print(self)


def nojus(position):
    return (
        evaluate_material(position)
        if position.turn == chess.WHITE
        else -evaluate_material(position)
    )


def evaluate_material(position):
    material_balance = 0

    for square in chess.SQUARES:
        piece = position.piece_at(square)
        if piece is not None:
            material_balance += piece_value(piece)

    return material_balance


def piece_value(piece):
    if piece.color == chess.WHITE:
        color_multiplier = 1
    else:
        color_multiplier = -1

    if piece.piece_type == chess.PAWN:
        return 1 * color_multiplier
    elif piece.piece_type == chess.KNIGHT:
        return 3 * color_multiplier
    elif piece.piece_type == chess.BISHOP:
        return 3 * color_multiplier
    elif piece.piece_type == chess.ROOK:
        return 5 * color_multiplier
    elif piece.piece_type == chess.QUEEN:
        return 9 * color_multiplier
    elif piece.piece_type == chess.KING:
        return 10000 * color_multiplier
