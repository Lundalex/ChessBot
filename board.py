import math
import pygame
import os

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
        self.pawnMoveOffsetsWhite = {
            "forwardOneWhite": 8,
            # "forwardTwoWhite": 16,
            "captureLeftWhite": 7,
            "captureRightWhite": 9
        }
        self.pawnMoveOffsetsBlack = {
            "forwardOneBlack": -8,
            # "forwardTwoBlack": -16,
            "captureLeftBlack": -7,
            "captureRightBlack": -9,
        }
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
    
    def MakeMove(self, fromSquare, toSquare):
        if (fromSquare != 64 and toSquare != 64):
            self.pcs[toSquare] = self.pcs[fromSquare]
            self.pcs[fromSquare] = 0

        return board

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
                legalMoves.update(self.__GetLegalMovesPawn(curSquare, pieceColor))
            if pieceCharLower == "n":
                legalMoves.update(self.__GetLegalMovesKnight(curSquare, pieceColor))
            elif pieceCharLower == "b":
                legalMoves.update(self.__GetLegalMovesBishop(curSquare, pieceColor))
            elif pieceCharLower == "r":
                legalMoves.update(self.__GetLegalMovesRook(curSquare, pieceColor))
            elif pieceCharLower == "q":
                legalMoves.update(self.__GetLegalMovesQueen(curSquare, pieceColor))
            elif pieceCharLower == "k":
                legalMoves.update(self.__GetLegalMovesKing(curSquare, pieceColor))

        return legalMoves

    def GetLegalMovesPiece(self, curSquare, pieceKey):
        legalMoves = set()

        pieceChar = GetPieceChar(pieceKey)
        pieceColor = 0b1000 if pieceChar.isupper() else 0b0000
        pieceCharLower = pieceChar.lower()

        if pieceCharLower == "p":
            legalMoves.update(self.__GetLegalMovesPawn(curSquare, pieceColor))
        if pieceCharLower == "n":
            legalMoves.update(self.__GetLegalMovesKnight(curSquare, pieceColor))
        elif pieceCharLower == "b":
            legalMoves.update(self.__GetLegalMovesBishop(curSquare, pieceColor))
        elif pieceCharLower == "r":
            legalMoves.update(self.__GetLegalMovesRook(curSquare, pieceColor))
        elif pieceCharLower == "q":
            legalMoves.update(self.__GetLegalMovesQueen(curSquare, pieceColor))
        elif pieceCharLower == "k":
            legalMoves.update(self.__GetLegalMovesKing(curSquare, pieceColor))

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
        offset = moveOffset
        dirLegalMoves = set()
        while (self.__CheckBoardPcsBounds(curSquare + offset) and 
            self.pcs[curSquare + offset] == 0 and 
            self.__CheckBounds(curSquare + offset - moveOffset, curSquare + offset)):
            
            dirLegalMoves.add((curSquare, curSquare + offset))
            offset += moveOffset
        if (self.__CheckBoardPcsBounds(curSquare + offset) and 
            self.pcs[curSquare + offset] & 0b1000 != color and
            self.__CheckBounds(curSquare + offset - moveOffset, curSquare + offset)):
            dirLegalMoves.add((curSquare, curSquare + offset))
        return dirLegalMoves

    def __GetLegalMovesKing(self, curSquare, color):
        kingLegalMoves = set()
        for kingMoveOffset in self.kingMoveOffsets.values():
            if (self.__CheckBoardPcsBounds(curSquare + kingMoveOffset)):
                if (self.pcs[curSquare + kingMoveOffset] & 0b1000 != color or
                    self.pcs[curSquare + kingMoveOffset] == 0):
                    kingLegalMoves.add((curSquare, curSquare + kingMoveOffset))
        return kingLegalMoves

    def __GetLegalMovesKnight(self, curSquare, color):
        knightLegalMoves = set()
        for knightMoveOffset in self.knightMoveOffsets.values():
            if (self.__CheckBoardPcsBounds(curSquare + knightMoveOffset)):
                if (self.pcs[curSquare + knightMoveOffset] & 0b1000 != color or
                    self.pcs[curSquare + knightMoveOffset] == 0):
                    knightLegalMoves.add((curSquare, curSquare + knightMoveOffset))
        return knightLegalMoves

    def __GetLegalMovesPawn(self, curSquare, color):
        pawnLegalMoves = set()
        if (color == 0b0000):
            for pawnMoveOffset in self.pawnMoveOffsetsWhite.values():
                if (self.__CheckBoardPcsBounds(curSquare + pawnMoveOffset)):
                    if (pawnMoveOffset == 8):
                        if (self.pcs[curSquare + pawnMoveOffset] == 0):
                            pawnLegalMoves.add((curSquare, curSquare + pawnMoveOffset))
                    else:
                        if (self.pcs[curSquare + pawnMoveOffset] & 0b1000 != color  and
                            self.pcs[curSquare + pawnMoveOffset] != 0):
                            pawnLegalMoves.add((curSquare, curSquare + pawnMoveOffset))
            return pawnLegalMoves
        else: # color == 0b0000
            for pawnMoveOffset in self.pawnMoveOffsetsBlack.values():
                if (self.__CheckBoardPcsBounds(curSquare + pawnMoveOffset)):
                    if (pawnMoveOffset == -8):
                        if (self.pcs[curSquare + pawnMoveOffset] == 0):
                            pawnLegalMoves.add((curSquare, curSquare + pawnMoveOffset))
                    else:
                        if (self.pcs[curSquare + pawnMoveOffset] & 0b1000 != color and
                            self.pcs[curSquare + pawnMoveOffset] != 0):
                            pawnLegalMoves.add((curSquare, curSquare + pawnMoveOffset))
            return pawnLegalMoves

        # self.pawnOffsets = {
        #     "forwardOneBlack": -8,
        #     "forwardTwoBlack": -16,
        #     "forwardOneWhite": 8,
        #     "forwardTwoWhite": 16,
        #     "captureLeftBlack": -7,
        #     "captureRightBlack": -9,
        #     "captureLeftWhite": 7,
        #     "captureRightWhite": 9
        # }

    def __CheckBounds(self, lastSquare, nextSquare):
        if (self.__CheckBoardPcsBounds(nextSquare) and -1 <= (lastSquare % 8 - nextSquare % 8) <= 1):
            return True
        return False
    
    def __CheckBoardPcsBounds(self, pieceIndex):
        if (0 <= pieceIndex <= 63):
            return True
        return False

class Interface:

    def __init__(self, boardList, legalMoves):
        self.boardPositions = boardList
        self.boardSize = 8
        self.squareSize = 80
        self.width = self.height = self.squareSize * self.boardSize
        self.fromSquare = 64
        self.toSquare = 64

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chess Bot")
        self.__LoadPieces()
        self.DrawBoard(legalMoves)

    def __LoadPieces(self):
        self.pieces = {}
        piece_names = [
            'n', 'q', 'r', 'b', 'k', 'p',
            'wN', 'wQ', 'wR', 'wB', 'wK', 'wP',
            'mn', 'mq', 'mr', 'mb', 'mk', 'mp',
            'mwN', 'mwQ', 'mwR', 'mwB', 'mwK', 'mwP'
        ]
        for piece in piece_names:
            self.pieces[piece] = pygame.image.load(os.path.join('ChessPieces', piece + '.png'))
            self.pieces[piece] = pygame.transform.scale(self.pieces[piece], (self.squareSize, self.squareSize))

    def DrawBoard(self, legalMoves):
        colors = [pygame.Color("white"), pygame.Color("gray"), pygame.Color("orange")]
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                boardIndex = row * 8 + col
                if (valueYInTuple(legalMoves, boardIndex)):
                    squareColor = colors[2]
                else:
                    squareColor = colors[((row + col) % 2)] 
                pieceChar = GetPieceChar(self.boardPositions[boardIndex])
                self.__DrawSquare(col, row, squareColor)
                self.__DrawPiece(row, col, pieceChar)
        self.FlipScreen()
    
    def __DrawSquare(self, col, row, squareColor):
        pygame.draw.rect(self.screen, squareColor, 
                        pygame.Rect(col*self.squareSize, row*self.squareSize, 
                        self.squareSize, self.squareSize))
        
    def RightClickAction(self, mousePosXY, colorKey, board):
        xSquare = math.floor(mousePosXY[0] / self.squareSize)
        ySquare = math.floor(mousePosXY[1] / self.squareSize)
        squareKey = ySquare * 8 + xSquare
        move = (64, 64)
        moveIsLegal = True
        if (self.fromSquare == 64):
            self.fromSquare = squareKey
            move = self.fromSquare, 64
        else:
            if ((fromSquare, squareKey) in board.GetLegalMoves(colorKey)):
                self.toSquare = squareKey
                move = self.fromSquare, self.toSquare
                self.fromSquare = 64
                self.toSquare = 64
            else:
                moveIsLegal = False
                self.fromSquare = 64
                self.toSquare = 64

        return move[0], move[1], moveIsLegal

    def __DrawPiece(self, row, col, pieceChar):
        if pieceChar.isupper():
            pieceChar = "w" + pieceChar
        if pieceChar in self.pieces:
            piece_image = self.pieces[pieceChar]
            self.screen.blit(piece_image, (col*self.squareSize, row*self.squareSize))
    
    def FlipScreen(self):
        pygame.display.flip()

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
        pieceType = "n"
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

def valueYInTuple(tupleSet, number):
    for a, b in tupleSet:
        if b == number:
            return True
    return False

board = Board()
board.SetStart()
board.UpdateBoardStr()
print(board.boardStr)
print(board.GetLegalMoves(0b1000))

colorTurn = 0b1000
interface = Interface(board.pcs, board.GetLegalMoves(colorTurn))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mousePos = pygame.mouse.get_pos()
                colorTurnCopy = 0b0000
                if (colorTurn == 0b0000):
                    colorTurnCopy = 0b1000
                fromSquare, toSquare, moveIsLegal = interface.RightClickAction(mousePos, colorTurn, board)
                if (not moveIsLegal):
                    continue
                if (toSquare != 64):
                    if (colorTurn == 0b0000):
                        colorTurn = 0b1000
                    else:
                        colorTurn = 0b0000
                    board.MakeMove(fromSquare, toSquare)
                    interface.DrawBoard(board.GetLegalMoves(colorTurn))
                else:
                    interface.DrawBoard(board.GetLegalMovesPiece(fromSquare, board.pcs[fromSquare]))
pygame.quit()