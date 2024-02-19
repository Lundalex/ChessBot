from math import floor

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

def StrMove(num):
    row = num % 8
    col = floor(num / 8)

    rowChar = ""
    if row == 0:
        rowChar = "a"
    elif row == 1:
        rowChar = "b"
    elif row == 2:
        rowChar = "c"
    elif row == 3:
        rowChar = "d"
    elif row == 4:
        rowChar = "e"
    elif row == 5:
        rowChar = "f"
    elif row == 6:
        rowChar = "g"
    elif row == 7:
        rowChar = "h"
    
    return rowChar + str(8- col)