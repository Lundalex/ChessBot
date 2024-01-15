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
        self.rookMoveOffsets = {
            "north": -8,
            "west": -1,
            "east": 1,
            "south": 8
        }
        self.bishopMoveOffsets = {
            "northWest": -9,
            "northEast": -7,
            "southwest": 7,
            "southEast": 9
        }
        self.queenMoveOffsets = {
            "north": -8,
            "west": -1,
            "east": 1,
            "south": 8,
            "northWest": -9,
            "northEast": -7,
            "southwest": 7,
            "southEast": 9
        }
        self.knightMoveOffsets = {
            "northWestLow": -10,
            "northWestHigh": -17,
            "northEastLow": -6,
            "northEastHigh": -15,
            "southWestLow": 15,
            "southWestHigh": 6,
            "southEastLow": 17,
            "southEastHigh": 10
        }
        self.kingMoveOffsets = self.queenMoveOffsets

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

    # Returns all legal moves for current piece positions
    def GetLegalMoves(self, colorKey):
        legalMoves = set()
        for curSquare, pieceKey in enumerate(self.pcs):
            pieceChar = GetPieceChar(pieceKey)
            pieceColor = 0b1000 if pieceChar.isupper() else 0b0000
            if (pieceColor != colorKey):
                continue
            pieceCharLower = pieceChar.lower()

            if pieceCharLower == "p":
                legalMoves.update(self.__GetLegalMovesPawn(curSquare, colorKey))
            elif pieceCharLower == "n":
                legalMoves.update(self.__GetLegalMovesKnight(curSquare, colorKey))
            elif pieceCharLower == "b":
                legalMoves.update(self.__GetLegalMovesBishop(curSquare, colorKey))
            elif pieceCharLower == "r":
                legalMoves.update(self.__GetLegalMovesRook(curSquare, colorKey))
            elif pieceCharLower == "q":
                legalMoves.update(self.__GetLegalMovesQueen(curSquare, colorKey))
            elif pieceCharLower == "k":
                legalMoves.update(self.__GetLegalMovesKing(curSquare, colorKey))

        return legalMoves

    def __GetLegalMovesQueen(self, curSquare, color):
        queenLegalMoves = set()
        for queenMoveOffset in self.queenMoveOffsets.values():
            queenLegalMoves.update(self.__GetLegalMovesInDirection(curSquare, color, queenMoveOffset))
        return queenLegalMoves

    def __GetLegalMovesRook(self, curSquare, color):
        rookLegalMoves = set()
        for rookMoveOffset in self.rookMoveOffsets.values():
            rookLegalMoves.update(self.__GetLegalMovesInDirection(curSquare, color, rookMoveOffset))
        return rookLegalMoves

    def __GetLegalMovesBishop(self, curSquare, color):
        bishopLegalMoves = set()
        for bishopMoveOffset in self.bishopMoveOffsets.values():
            bishopLegalMoves.update(self.__GetLegalMovesInDirection(curSquare, color, bishopMoveOffset))
        return bishopLegalMoves
    
    def __GetLegalMovesInDirection(self, curSquare, color, moveOffset):
        offset = 0
        dirLegalMoves = set()
        while (0 <= curSquare + offset < len(self.pcs) and 
            self.pcs[curSquare + offset] == 0b0000 and 
            self.__CheckBounds(curSquare + offset - moveOffset, curSquare + offset)):
            dirLegalMoves.add((curSquare, curSquare+offset))
            offset += moveOffset
        if (0 <= curSquare + offset < len(self.pcs) and 
            self.__CheckBounds(curSquare + offset - moveOffset, curSquare + offset)):
            dirLegalMoves.add((curSquare, curSquare+offset))
        return dirLegalMoves

    def __GetLegalMovesKing(self, curSquare, color):
        kingLegalMoves = set()
        for kingMoveOffset in self.kingMoveOffsets.values():
            if (self.__CheckBoardPcsBounds(curSquare + kingMoveOffset)):
                if (self.pcs[curSquare + kingMoveOffset] & color != 0):
                    kingLegalMoves.add((curSquare, curSquare + kingMoveOffset))
        return kingLegalMoves

    def __GetLegalMovesKnight(self, curSquare, color):
        knightLegalMoves = set()
        for knightMoveOffset in self.knightMoveOffsets.values():
            if (self.__CheckBoardPcsBounds(curSquare + knightMoveOffset)):
                if (self.pcs[curSquare + knightMoveOffset] & color != 0):
                    knightLegalMoves.add((curSquare, curSquare + knightMoveOffset))
        return knightLegalMoves

    def __GetLegalMovesPawn(self, curSquare, color):
        return set()

    def __CheckBounds(self, lastSquare, nextSquare):
        if (self.__CheckBoardPcsBounds(nextSquare) and -1 <= (lastSquare % 8 - nextSquare % 8) <= 1):
            return True
        return False
    
    def __CheckBoardPcsBounds(self, pieceIndex):
        if (0 <= pieceIndex <= 63):
            return True
        return False

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
print(board.GetLegalMoves(0b1000))
# pieceKey = board.pcs[23]
# print(pieceKey)
# print(GetPieceChar(pieceKey))
# print(pieceKey)
# print(GetPieceChar(pieceKey))