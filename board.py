import math
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

from testing import *
from chess_utils import *


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
        self.colorTurn = 0b1000
        for _ in range(64):
            # abc -> Piece key
            # d -> Piece color
            self.pcs.append(0b0000)
        self.pawnMoveOffsetsWhite = {
            "forwardOneWhite": 8,
            "forwardTwoWhite": 16,
            "captureLeftWhite": 7,
            "captureRightWhite": 9,
        }
        self.pawnMoveOffsetsBlack = {
            "forwardOneBlack": -8,
            "forwardTwoBlack": -16,
            "captureLeftBlack": -7,
            "captureRightBlack": -9,
        }
        self.rookMoveOffsets = {"north": -8, "west": -1, "east": 1, "south": 8}
        self.bishopMoveOffsets = {
            "northWest": -9,
            "northEast": -7,
            "southwest": 7,
            "southEast": 9,
        }
        self.queenMoveOffsets = {
            "north": -8,
            "west": -1,
            "east": 1,
            "south": 8,
            "northWest": -9,
            "northEast": -7,
            "southwest": 7,
            "southEast": 9,
        }
        self.knightMoveOffsets = {
            "northWestLow": -10,
            "northWestHigh": -17,
            "northEastLow": -6,
            "northEastHigh": -15,
            "southWestLow": 15,
            "southWestHigh": 6,
            "southEastLow": 17,
            "southEastHigh": 10,
        }
        self.kingMoveOffsets = self.queenMoveOffsets

    # Set variables to given data
    def SetBoard(
        self,
        startBoard,
        turnToMove,
        castleAvailability,
        enPessantTargetSquare,
        halfmoves,
        fullmoves,
    ):
        self.pcs = startBoard
        self.turnToMove = turnToMove
        self.castleAvailability = castleAvailability
        self.enPessantTargetSquare = enPessantTargetSquare
        self.halfmoves = halfmoves
        self.fullmoves = fullmoves

    # Set variables to starting data
    def SetStart(self):
        #      white   black
        P, p = 0b0001, 0b1001
        N, n = 0b0010, 0b1010
        B, b = 0b0011, 0b1011
        R, r = 0b0100, 0b1100
        Q, q = 0b0101, 0b1101
        K, k = 0b0110, 0b1110

        startconfiguration = [
            R,
            N,
            B,
            Q,
            K,
            B,
            N,
            R,
            P,
            P,
            P,
            P,
            P,
            P,
            P,
            P,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            p,
            p,
            p,
            p,
            p,
            p,
            p,
            p,
            r,
            n,
            b,
            q,
            k,
            b,
            n,
            r,
        ]

        self.SetBoard(startconfiguration, "w", "KQkq", 0, 0, 0)

    def MakeMove(self, fromSquare, toSquare):
        # 64: No square selected
        if fromSquare != 64 and toSquare != 64:
            self.pcs[toSquare] = self.pcs[fromSquare]
            # 0: No piece on the square
            self.pcs[fromSquare] = 0

        if self.colorTurn == 0b0000:
            self.colorTurn = 0b1000
        else:
            self.colorTurn = 0b0000
        return board

    # Updates the self.boardStr variable
    def UpdateBoardStr(self):
        if not self.pcs:
            raise ValueError("Board is empty -> no pieces to get positions for")

        boardStr = ""
        emptyIndeces = 0
        # Algorithm for generating the string for board positions.
        # Example: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0
        for i, pieceKey in enumerate(self.pcs):
            # New row
            if (i) % 8 == 0 and i != 0:
                if emptyIndeces != 0:
                    boardStr += str(emptyIndeces)
                    emptyIndeces = 0
                boardStr += "/"

            # Empty square
            if pieceKey == 0b0000:
                emptyIndeces += 1
                continue

            # Piece on square
            pieceChar = GetPieceChar(pieceKey)
            if emptyIndeces != 0:
                boardStr += str(emptyIndeces)
                emptyIndeces = 0
            boardStr += pieceChar

        # Add per turn data
        enPessantTargetSquareStr = (
            str(self.enPessantTargetSquare) if self.enPessantTargetSquare != 0 else "-"
        )

        # Add per game data
        boardStr += (
            " "
            + self.turnToMove
            + " "
            + self.castleAvailability
            + " "
            + enPessantTargetSquareStr
            + " "
            + str(self.halfmoves)
            + " "
            + str(self.fullmoves)
        )

        self.boardStr = boardStr

    # Updates the self.boardStr variable, AND returns it
    # Note: For modifications of boardStr, using UpdateBoardStr directly is more efficient
    def GetBoardStr(self):
        self.SetBoardStr()
        return self.boardStr

    # Returns whether a specific move is legal or not
    def IsMoveValidCheckConsidered(self, fromSquare, toSquare, colorKey):
        # Simulate the move
        originalPiece = self.pcs[toSquare]
        self.pcs[toSquare] = self.pcs[fromSquare]
        self.pcs[fromSquare] = 0

        # Check if the king is in check after the move
        kingInCheck = self.IsKingInCheck(colorKey)

        # Revert the simulated move
        self.pcs[fromSquare] = self.pcs[toSquare]
        self.pcs[toSquare] = originalPiece

        return not kingInCheck

    # Returns all legal moves (considering checks)
    def GetLegalMovesCheckConsidered(self, colorKey):
        legalMoves = self.GetLegalMoves(
            colorKey
        )  # Get all legal moves (without considering checks)
        legalMovesCheckConsidered = set()

        # For each possible move, remove all moves that do not place the same-colored king in check
        for fromSquare, toSquare in legalMoves:
            if self.IsMoveValidCheckConsidered(fromSquare, toSquare, colorKey):
                legalMovesCheckConsidered.add((fromSquare, toSquare))

        return legalMovesCheckConsidered

    # Check if the king is in check for the current piece configuration
    def IsKingInCheck(self, colorKey):
        kingSquare = self.GetKingSquare(colorKey)
        opponentColorKey = 0b0000 if colorKey == 0b1000 else 0b1000
        opponentMoves = self.__GetLegalMovesFromPcs(self.pcs, opponentColorKey)

        # Check if any one of the oppenents's moves can capture the king
        for _, toSquare in opponentMoves:
            if toSquare == kingSquare:
                return True
        return False

    # Returns all legal moves for current piece positions (without considering checks)
    def GetLegalMoves(self, colorKey):
        legalMoves = self.__GetLegalMovesFromPcs(self.pcs, colorKey)

        return legalMoves

    # Returns all legal moves for a specific piece
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

        legalMovesCheckConsidered = set()

        for fromSquare, toSquare in legalMoves:
            if self.IsMoveValidCheckConsidered(fromSquare, toSquare, pieceColor):
                legalMovesCheckConsidered.add((fromSquare, toSquare))

        return legalMovesCheckConsidered

    # Returns whether or not the current piece configuration results in a checkmate
    def IsCheckmate(self, colorKey):
        if not self.IsKingInCheck(colorKey):
            return False  # Not in check, so it can't be checkmate

        # Try to find any legal move that can get the king out of check
        for fromSquare in range(64):
            pieceKey = self.pcs[fromSquare]
            if pieceKey != 0 and (pieceKey & 0b1000) == colorKey:
                legalMoves = self.GetLegalMovesPiece(fromSquare, pieceKey)
                for _, toSquare in legalMoves:
                    if self.IsMoveValidCheckConsidered(fromSquare, toSquare, colorKey):
                        return False  # Found a move that can get the king out of check

        return True  # No moves available to get the king out of check -> Checkmate!

    def GetKingSquare(self, color):
        for i, pieceKey in enumerate(self.pcs):
            # Corrected to check specifically for the king
            if pieceKey & 0b0111 == 0b0110 and pieceKey & 0b1000 == color:
                return i
        raise ValueError(
            "No king of colorKey", color, "found -> no legal moves can be generated"
        )

    # -- Helper functions --
    # (These functions can only be called from within this class)

    def __GetLegalMovesFromPcs(self, pcs, colorKey):
        legalMoves = set()
        for curSquare, pieceKey in enumerate(pcs):
            pieceChar = GetPieceChar(pieceKey)
            pieceColor = 0b1000 if pieceChar.isupper() else 0b0000

            # Only get legal moves for the chosen color
            if pieceColor != colorKey:
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

    def __GetLegalMovesQueen(self, curSquare, color):
        queenLegalMoves = set()
        for queenMoveOffset in self.queenMoveOffsets.values():
            queenLegalMoves.update(
                self.__GetLegalMovesInDirection(curSquare, color, queenMoveOffset)
            )
        return queenLegalMoves

    def __GetLegalMovesRook(self, curSquare, color):
        rookLegalMoves = set()
        for rookMoveOffset in self.rookMoveOffsets.values():
            rookLegalMoves.update(
                self.__GetLegalMovesInDirection(curSquare, color, rookMoveOffset)
            )
        return rookLegalMoves

    def __GetLegalMovesBishop(self, curSquare, color):
        bishopLegalMoves = set()
        for bishopMoveOffset in self.bishopMoveOffsets.values():
            bishopLegalMoves.update(
                self.__GetLegalMovesInDirection(curSquare, color, bishopMoveOffset)
            )
        return bishopLegalMoves

    def __GetLegalMovesInDirection(self, curSquare, color, moveOffset):
        offset = moveOffset
        dirLegalMoves = set()
        while (
            self.__CheckBoardPcsBounds(curSquare + offset)
            and self.pcs[curSquare + offset] == 0
            and self.__CheckBounds(curSquare + offset - moveOffset, curSquare + offset)
        ):
            dirLegalMoves.add((curSquare, curSquare + offset))
            offset += moveOffset
        if (
            self.__CheckBoardPcsBounds(curSquare + offset)
            and self.pcs[curSquare + offset] & 0b1000 != color
            and self.__CheckBounds(curSquare + offset - moveOffset, curSquare + offset)
        ):
            dirLegalMoves.add((curSquare, curSquare + offset))
        return dirLegalMoves

    def __GetLegalMovesKing(self, curSquare, color):
        kingLegalMoves = set()
        for kingMoveOffset in self.kingMoveOffsets.values():
            if self.__CheckBoardPcsBounds(
                curSquare + kingMoveOffset
            ) and self.__CheckBounds(curSquare, curSquare + kingMoveOffset):
                if (
                    self.pcs[curSquare + kingMoveOffset] & 0b1000 != color
                    or self.pcs[curSquare + kingMoveOffset] == 0
                ):
                    kingLegalMoves.add((curSquare, curSquare + kingMoveOffset))
        return kingLegalMoves

    def __GetLegalMovesKnight(self, curSquare, color):
        knightLegalMoves = set()
        for knightMoveOffset in self.knightMoveOffsets.values():
            if self.__CheckBoardPcsBounds(
                curSquare + knightMoveOffset
            ) and self.__CheckBoundsKnight(curSquare, curSquare + knightMoveOffset):
                if (
                    self.pcs[curSquare + knightMoveOffset] & 0b1000 != color
                    or self.pcs[curSquare + knightMoveOffset] == 0
                ):
                    knightLegalMoves.add((curSquare, curSquare + knightMoveOffset))
        return knightLegalMoves

    def __GetLegalMovesPawn(self, curSquare, color):
        pawnLegalMoves = set()
        startingRows = {
            0b0000: range(8, 16),  # White pawns starting row
            0b1000: range(48, 56),  # Black pawns starting row
        }
        if color == 0b0000:  # White pawn
            for moveName, pawnMoveOffset in self.pawnMoveOffsetsWhite.items():
                targetSquare = curSquare + pawnMoveOffset
                if self.__CheckBoardPcsBounds(targetSquare):
                    if "forwardOne" in moveName and self.pcs[targetSquare] == 0:
                        pawnLegalMoves.add((curSquare, targetSquare))
                    elif (
                        "forwardTwoWhite" in moveName
                        and curSquare in startingRows[color]
                        and self.pcs[curSquare + 8] == 0
                        and self.pcs[targetSquare] == 0
                    ):
                        # Ensure the pawn is making its first move by checking its position
                        pawnLegalMoves.add((curSquare, targetSquare))
                    elif "capture" in moveName:
                        if (
                            self.pcs[targetSquare] & 0b1000 != color
                            and self.pcs[targetSquare] != 0
                        ):
                            pawnLegalMoves.add((curSquare, targetSquare))
        else:  # Black pawn
            for moveName, pawnMoveOffset in self.pawnMoveOffsetsBlack.items():
                targetSquare = curSquare + pawnMoveOffset
                if self.__CheckBoardPcsBounds(targetSquare):
                    if "forwardOne" in moveName and self.pcs[targetSquare] == 0:
                        pawnLegalMoves.add((curSquare, targetSquare))
                    elif (
                        "forwardTwoBlack" in moveName
                        and curSquare in startingRows[color]
                        and self.pcs[curSquare - 8] == 0
                        and self.pcs[targetSquare] == 0
                    ):
                        # Ensure the pawn is making its first move by checking its position
                        pawnLegalMoves.add((curSquare, targetSquare))
                    elif "capture" in moveName:
                        if (
                            self.pcs[targetSquare] & 0b1000 != color
                            and self.pcs[targetSquare] != 0
                        ):
                            pawnLegalMoves.add((curSquare, targetSquare))
        return pawnLegalMoves

    def __CheckBounds(self, lastSquare, nextSquare):
        if (
            self.__CheckBoardPcsBounds(nextSquare)
            and -1 <= (lastSquare % 8 - nextSquare % 8) <= 1
        ):
            return True
        return False

    # Modified version of __CheckBounds() to accomodate for the knight being able to move up to 2 collumns / 2 rows
    def __CheckBoundsKnight(self, lastSquare, nextSquare):
        if (
            self.__CheckBoardPcsBounds(nextSquare)
            and -2 <= (lastSquare % 8 - nextSquare % 8) <= 2
        ):
            return True
        return False

    def __CheckBoardPcsBounds(self, pieceIndex):
        if 0 <= pieceIndex <= 63:
            return True
        return False

    # -- AI functions --
    # (These functions will send data to our AI model)

    # Returns the approximated board evaluation
    def GetEvaluation(self):
        return "yes"


class Interface:
    # Initializes Interface variables
    def __init__(self, board, squareSize):
        self.boardPositions = board.pcs
        self.boardSize = 8
        self.squareSize = squareSize
        self.width = self.height = self.squareSize * self.boardSize
        self.fromSquare = 64
        self.toSquare = 64

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chess Bot")
        self.__LoadPieces()
        self.DrawBoard(board.GetLegalMoves(board.colorTurn))

    # Set self board position data
    def SetBoardPositions(self, boardList):
        self.boardPositions = boardList

    # Note: "RightClickAction()" is more efficient and should be used for user-made moves
    # This function should only be used to do the AI-made moves
    def SetBoardPositionsAndDrawBoard(self, board, colorTurn=0b1000):
        self.SetBoardPositions(board.pcs)
        self.DrawBoard(board.GetLegalMoves(colorTurn))

    # Draws the whole board using pieces configuration
    # Also highlights any possible moves for the user
    def DrawBoard(self, legalMoves):
        colors = [pygame.Color("white"), pygame.Color("gray"), pygame.Color("orange")]
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                boardIndex = row * 8 + col
                if valueYInTuple(legalMoves, boardIndex):
                    squareColor = colors[2]
                else:
                    squareColor = colors[((row + col) % 2)]
                pieceChar = GetPieceChar(self.boardPositions[boardIndex])
                self.__DrawSquare(col, row, squareColor)
                self.__DrawPiece(row, col, pieceChar)
        pygame.display.flip()

    # Converts a mouse click to a board move
    def RightClickAction(self, mousePosXY, colorKey, board):
        # Get the clicked square on the board grid
        xSquare = math.floor(mousePosXY[0] / self.squareSize)
        ySquare = math.floor(mousePosXY[1] / self.squareSize)

        squareKey = ySquare * 8 + xSquare

        # 64: No square
        move = (64, 64)
        moveIsLegal = True

        # Set fromSquare variable
        if self.fromSquare == 64:
            self.fromSquare = squareKey
            move = self.fromSquare, 64

        # Set toSquare variable (if the move is legal)
        else:
            if (fromSquare, squareKey) in board.GetLegalMovesCheckConsidered(colorKey):
                self.toSquare = squareKey
                move = self.fromSquare, self.toSquare
                self.fromSquare = 64
                self.toSquare = 64
            else:
                moveIsLegal = False
                self.fromSquare = 64
                self.toSquare = 64

        return move[0], move[1], moveIsLegal

    # Renders a message to the user interface
    def DisplayMessage(self, message):
        pygame.font.init()
        font = pygame.font.Font(None, 80)
        textSurface = font.render(message, True, (255, 0, 0))
        textRect = textSurface.get_rect(center=(self.width // 2, self.height - 60))
        self.screen.blit(textSurface, textRect)
        pygame.display.flip()

    # Render the checkmate animation (4 seconds)
    def DisplayWinner(self, board, colorKey, displayMessage):
        # Find the king's position for the given color
        kingSquare = board.GetKingSquare(colorKey)
        kingRow, kingCol = divmod(kingSquare, 8)

        endTime = pygame.time.get_ticks() + 4000
        flashDuration = 200
        lastFlashTime = pygame.time.get_ticks()
        flashOn = True

        while pygame.time.get_ticks() < endTime:
            currentTime = pygame.time.get_ticks()
            if currentTime - lastFlashTime > flashDuration:
                flashOn = not flashOn  # Toggle flash state
                lastFlashTime = currentTime

                if flashOn:
                    # Draw the king's square in red
                    self.__DrawSquare(kingCol, kingRow, pygame.Color("red"))
                    self.__DrawPiece(
                        kingRow, kingCol, GetPieceChar(board.pcs[kingSquare])
                    )
                else:
                    # Redraw the board as it normally appears
                    self.DrawBoard(board.GetLegalMoves(colorKey))

                pygame.display.flip()

        self.DisplayMessage(displayMessage)

    # -- Helper functions --
    # (These functions can only be called from within this class)

    def __LoadPieces(self):
        self.pieces = {}
        piece_names = [
            "n",
            "q",
            "r",
            "b",
            "k",
            "p",
            "wN",
            "wQ",
            "wR",
            "wB",
            "wK",
            "wP",
            "mn",
            "mq",
            "mr",
            "mb",
            "mk",
            "mp",
            "mwN",
            "mwQ",
            "mwR",
            "mwB",
            "mwK",
            "mwP",
        ]
        for piece in piece_names:
            self.pieces[piece] = pygame.image.load(
                os.path.join("ChessPieces", piece + ".png")
            )
            self.pieces[piece] = pygame.transform.scale(
                self.pieces[piece], (self.squareSize, self.squareSize)
            )

    def __DrawSquare(self, col, row, squareColor):
        pygame.draw.rect(
            self.screen,
            squareColor,
            pygame.Rect(
                col * self.squareSize,
                row * self.squareSize,
                self.squareSize,
                self.squareSize,
            ),
        )

    def __DrawPiece(self, row, col, pieceChar):
        if pieceChar.isupper():
            pieceChar = "w" + pieceChar
        if pieceChar in self.pieces:
            piece_image = self.pieces[pieceChar]
            self.screen.blit(
                piece_image, (col * self.squareSize, row * self.squareSize)
            )


board = Board()
interface = Interface(board, 100)
running = True
isCheckMate = False

# playAgainstBot = True -> Play against the bot
# playAgainstBot = False -> Play against another player (local)
playAgainstBot = False

# Resets board, interface and game data
def ResetBoard():
    global board, interface, isCheckMate
    board = Board()
    board.SetStart()
    board.UpdateBoardStr()
    interface = Interface(board, 100)
    isCheckMate = False
    
    # Bot does the first move (white)
    if playAgainstBot:
        board.MakeMove(*[int(i) for i in read().split(",")])

def MakeBotMove():
    write(StrMove(fromSquare) + StrMove(toSquare))
    board.MakeMove(*[int(i) for i in read().split(",")])
    interface.DrawBoard(board.GetLegalMoves(board.colorTurn))
    
ResetBoard()  # Initial board setup

while running:
    for event in pygame.event.get():
        
        # Quit the program if the pygame window is closed
        if event.type == pygame.QUIT:
            running = False
            
        # Quit the program if the pygame window is closed
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            ResetBoard()
            
        # Handle move on user mouse click action
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not isCheckMate:
            
            mousePos = pygame.mouse.get_pos()
            board.colorTurnCopy = 0b1000 if board.colorTurn == 0b0000 else 0b0000
            
            # Get move data from mouse click data
            fromSquare, toSquare, moveIsLegal = interface.RightClickAction(mousePos, board.colorTurn, board)
            
            # Do nothing with the board if the move isn't legal
            if not moveIsLegal:
                continue
            
            # Make the move and render new piece configuration to the screen
            if toSquare != 64:
                board.MakeMove(fromSquare, toSquare)
                interface.DrawBoard(board.GetLegalMoves(board.colorTurn))
                if playAgainstBot:
                    MakeBotMove()
            else:
                interface.DrawBoard(board.GetLegalMovesPiece(fromSquare, board.pcs[fromSquare]))

            # Check for checkmate after each move
            if board.IsCheckmate(board.colorTurn):
                winnerColor = "White" if board.colorTurn == 0b0000 else "Black"  # This could be removed if not used
                interface.DisplayWinner(board, board.colorTurn, "Press RETURN to reset")
                isCheckMate = True

pygame.quit()
