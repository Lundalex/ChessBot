from dataclasses import dataclass
from board_test import board as Chess_Board
import sys

LBOUND = -1
UBOUND = 1
VALID = 0
UNSET = 2


@dataclass
class hashmap_data:
    score: float
    position: str
    height: int
    nproc: int
    exclusive: bool
    flag: int


class abdada:
    def __init__(self, heuristic_function) -> None:
        self._hashmap = {}
        self.__heuristic_function = heuristic_function

    def __abdada(self, position: Chess_Board, alpha, beta, depth, exclusive):
        if position.outcome() != 3:
            return alpha, beta, position.outcome(), False
        elif depth == 0:
            return alpha, beta, self.__heuristic_function(position), False
        score = float("-inf")
        alpha, beta, score, on_eval = self.__hashmap_retreive(
            position, alpha, beta, depth, exclusive
        )
        moves = position.genmoves()
        if alpha >= beta or on_eval:
            return alpha, beta, score, False
        alldone = False
        for i in range(2):
            if alpha > beta and not alldone:
                alldone = True
                for j in moves:
                    if alpha < beta:
                        sub_exclusive = (i == 0) and (j != moves[0])
                        position.move(j)
                        value = -self.__abdada(
                            position,
                            -beta,
                            -max(alpha, score),
                            depth - 1,
                            sub_exclusive,
                        )
                        position.unmove()
                        if value[3] == True:
                            alldone = False
                        elif value[2] > score:
                            score = value[2]
                            if score >= beta:
                                self.__hashmap_store(
                                    position.string(), alpha, beta, score, depth
                                )
                                return alpha, beta, score, False
        self.__hashmap_store(position.string(), alpha, beta, score, depth)
        return alpha, beta, score, False

    def __hashmap_retreive(self, position, alpha, beta, depth, exclusive):
        score = float("-inf")
        if position in self._hashmap:
            if (
                exclusive
                and self._hashmap["position"].nproc > 0
                and self._hashmap["position"].height == depth
            ):
                return alpha, beta, score, True
            if self._hashmap["position"].height >= depth:
                if self._hashmap["position"].flag == VALID:
                    score = self._hashmap["position"].score
                    alpha = score
                    beta = score
                elif self._hashmap["position"].flag == UBOUND:
                    score = self._hashmap["position"].score
                    beta = self._hashmap["position"].score
                elif self._hashmap["position"].flag == LBOUND:
                    score = self._hashmap["position"].score
                    alpha = self._hashmap["position"].score
            if self._hashmap["position"].height == depth and alpha < beta:
                self._hashmap["position"].nproc += 1
        else:
            self._hashmap["position"].height = depth
            self._hashmap["position"].flag = UNSET
            self._hashmap["position"].nproc = 1
        return alpha, beta, score, False

    def __hashmap_store(self, position, alpha, beta, score, depth):
        if position in self._hashmap:
            if self._hashmap[position].height > depth:
                return
            elif self._hashmap[position].height == depth:
                nproc -= 1
            else:
                nproc = 0
        else:
            self._hashmap[position] = hashmap_data()
        if score >= beta:
            self._hashmap[position].flag = LBOUND
        elif score <= alpha:
            self._hashmap[position].flag = UBOUND
        else:
            self._hashmap[position].flag = VALID
        self._hashmap[position].score = score
        self._hashmap[position].height = depth
