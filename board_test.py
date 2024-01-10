import chess


class board(chess.Board):
    def __init__(self):
        super.__init__()

    def genmoves(self):
        return tuple(super.legal_moves)

    def outcome(self):
        # a = super.Outcome(color)
        pass
