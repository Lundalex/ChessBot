from dataclasses import dataclass


LBOUND = -1
UBOUND = 1
VALID = 0

@dataclass
class board():
    board: tuple
    turn: bool
    castle: str
    en_passant: tuple
    half_moves: 
    full: str  


@dataclass
class stored_hashmap:
    position: board
    height: int
    nproc: int
    exclusive: bool
    flag: int
    

class abdada():
    def __init__(self, heuristic_function) -> None:
        self._hashmap = {}
        self.__heuristic_function = heuristic_function
    def hashmap_store(self, position, alpha, beta, score, depth):
        if position in self._hashmap:
            if self._hashmap[position].height > depth:
                return
            elif self._hashmap[position].height == depth:
                nproc -= 1
            else:
                nproc = 0 
        if score >= beta:
            self._hashmap[position] = LBOUND
        elif score <= alpha:
            self._hashmap[position] = UBOUND
        else:
            self._hashmap[position] = VALID
        

        

        