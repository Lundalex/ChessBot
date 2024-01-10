class Board:

    # initializes variables
    def __init__(self):
        self.pcs = []
        self.boardStr = " "
        self.turnToMove = " "
        self.castleAvailability = "    "
        self.enPessantTargetSquare = 0
        self.halfmoves = 0
        self.fullmoves = 0
        for _ in range(64):
            # abc -> Piece key
            # d -> Piece color
            self.pcs.append(0b0000)

    # Set variables to given data
    def SetBoard(self, startBoard, turnToMove, castleAvailability, enPessantTargetSquare, halfmoves, fullmoves):
        self.pcs = startBoard
        self.turnToMove = turnToMove
        self.castleAvailability = castleAvailability
        self.enPessantTargetSquare = enPessantTargetSquare
        self.halfmoves = halfmoves
        self.fullmoves = fullmoves

    # Set variables to starting data
    def SetStart(self):
        # white      black
        P, p = 0b0001, 0b1001
        N, n = 0b0010, 0b1010
        B, b = 0b0011, 0b1011
        R, r = 0b0100, 0b1100
        Q, q = 0b0101, 0b1101
        K, k = 0b0110, 0b1110

        startConfig = [
            R, N, B, Q, K, B, N, R,
            P, P, P, P, P, P, P, P,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            p, p, p, p, p, p, p, p,
            r, n, b, q, k, b, n, r,
        ]

        self.SetBoard(startConfig, "w", "KQkq", 0, 0, 0)

    # Updates the self.boardStr variable
    def UpdateBoardStr(self):
        
        if not self.pcs:
            raise ValueError("Board is empty, no pieces to get positions for.")
        
        boardStr = ""
        emptyIndeces = 0
        for i in range(64):
            pieceKey = self.pcs[i]

            if (i) % 8 == 0 and i != 0:
                if emptyIndeces != 0:
                    boardStr += str(emptyIndeces)
                    emptyIndeces = 0
                boardStr += "/"

            if pieceKey == 0b0000:
                emptyIndeces += 1
                continue

            pieceChar = GetPieceChar(pieceKey)
            if emptyIndeces != 0:
                boardStr += str(emptyIndeces)
                emptyIndeces = 0
            boardStr += pieceChar
        
        enPessantTargetSquareStr = str(self.enPessantTargetSquare) if self.enPessantTargetSquare != 0 else "-"
        boardStr += " " + self.turnToMove + " " + self.castleAvailability + " " + enPessantTargetSquareStr + " " + str(self.halfmoves) + " " + str(self.fullmoves)
         
        self.boardStr = boardStr
    
    # Updates the self.boardStr variable, AND returns it
    # Note: Accessing/modifying the self.boardStr variable directly is oftentimes more efficient
    def GetBoardStr(self):
        self.SetBoardStr()
        return self.boardStr

    # Returns the evaluated board evaluation
    def GetEvaluation(self):
        return "yes"

    # Returns all legal moves
    def GetLegalMoves(self):
        return "yes"


def GetPieceKey(pieceChar):

    pieceColor = 0b1000 if pieceChar.isupper() else 0b0000
    pieceChar = pieceChar.lower()

    pieceType = 0b0
    if pieceChar == "p":
        pieceType = 0b0001
    elif pieceChar == "n":
        pieceType = 0b0010
    elif pieceChar == "b":
        pieceType = 0b0011
    elif pieceChar == "r":
        pieceType = 0b0100
    elif pieceChar == "q":
        pieceType = 0b0101
    elif pieceChar == "k":
        pieceType = 0b0110
    
    return pieceType + pieceColor

def GetPieceChar(pieceKey):

    upperCase = True if pieceKey & 0b1000 else False

    pieceType = ""
    pieceTypeBin = pieceKey & 0b0111
    if pieceTypeBin == 0b0001:
        pieceType = "p"
    elif pieceTypeBin == 0b0010:
        pieceType = "k"
    elif pieceTypeBin == 0b0011:
        pieceType = "b"
    elif pieceTypeBin == 0b0100:
        pieceType = "r"
    elif pieceTypeBin == 0b0101:
        pieceType = "q"
    elif pieceTypeBin == 0b0110:
        pieceType = "k"
    else:
        return "empty"

    return pieceType.upper() if upperCase == True else pieceType



board = Board()
board.SetStart()
board.UpdateBoardStr()
print(board.boardStr)
# pieceKey = board.pcs[23]
# print(pieceKey)
# print(GetPieceChar(pieceKey))
# print(pieceKey)
# print(GetPieceChar(pieceKey))