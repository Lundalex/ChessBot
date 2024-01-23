from dataclasses import dataclass
from typing import Any
from board_test import AbdadaBoard as Chess_Board
from board_test import nojus, evaluate_material
import sys
from multiprocessing import Manager
from multiprocessing.pool import Pool
from copy import deepcopy as copy
from random import randint

LBOUND = -1
UBOUND = 1
VALID = 0
UNSET = 2


@dataclass
class hashmap_data:
    score: float
    height: int
    nproc: int
    flag: int


class abdada:
    def __init__(
        self,
        heuristic_function,
        depth: int = 4,
        n_threads: int = 1,
        debug: bool = False,
    ) -> None:
        self.n_threads = n_threads
        self.__heuristic_function = heuristic_function
        self.depth = depth
        try:
            manager = getattr(type(self), "manager")
        except AttributeError:
            manager = type(self).manager = Manager()
        self._whole_hashmap = manager.dict()

    def __start_abdada(self, position: Chess_Board, depth, hashmap):
        # a = randint(0, 69420)
        exclusive = False
        alpha = float("-inf")
        beta = float("inf")
        score = float("-inf")
        moves = position.genmoves()
        alldone = False
        # print("hej hej")
        list_of_done_moves = []
        for i in range(2):
            # print(alldone, alpha > beta)
            if alpha < beta and not alldone:
                # print(i)
                alldone = True
                for j in moves:
                    if alpha < beta:
                        sub_exclusive = (i == 0) and (j != moves[0])
                        position.move(j)
                        # self.__print(f"{position}, {depth}, cinq")
                        value = self.__abdada(
                            position,
                            -beta,
                            -max(alpha, score),
                            depth - 1,
                            sub_exclusive,
                        )
                        # print(f"{j}, {value[2]} inner moves")
                        # list_of_done_moves.append((j, value))
                        position.unmove()
                        if value[3] == True:
                            alldone = False
                        elif value[2] > score:
                            score = value[2]
                            move = j
                            if score >= beta:
                                self.__hashmap_store(
                                    position.string(),
                                    alpha,
                                    beta,
                                    score,
                                    depth,
                                    hashmap,
                                )
                                return score, move
                        # print(a, " ", j, " ", value, " ", score)
        self.__hashmap_store(position.string(), alpha, beta, score, depth, hashmap)
        # print(move)
        return score, move

    def __abdada(self, position: Chess_Board, alpha, beta, depth, exclusive, hashmap):
        # self.__print("hello")
        # self.__print(f"{position}, {depth}, {alpha}, {beta}, {exclusive} quatre")
        if position.outcome() != 3:
            # print(position.string())
            return alpha, beta, -position.outcome() * 99999999, False
        elif depth == 0:
            # if abs(self.__heuristic_function(position)) == 1:
            #    print(position.string(), end="\n\n")
            return alpha, beta, -self.__heuristic_function(position), False
        score = float("-inf")
        alpha, beta, score, on_eval = self.__hashmap_retreive(
            position.string(), alpha, beta, depth, exclusive, hashmap
        )
        moves = position.genmoves()
        if on_eval:
            return alpha, beta, -score, True
        elif alpha >= beta:
            return alpha, beta, -score, False
        alldone = False
        for i in range(2):
            if alpha < beta and not alldone:
                alldone = True
                for j in moves:
                    if alpha < beta:
                        sub_exclusive = (i == 0) and (j != moves[0])
                        position.move(j)
                        value = self.__abdada(
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
                                    position.string(),
                                    alpha,
                                    beta,
                                    score,
                                    depth,
                                    hashmap,
                                )
                                return alpha, beta, -score, False
        self.__hashmap_store(position.string(), alpha, beta, score, depth, hashmap)
        return alpha, beta, -score, False

    def __hashmap_retreive(self, position, alpha, beta, depth, exclusive, hashmap):
        score = float("-inf")
        with self.lock:
            if position in hashmap:
                if (
                    exclusive
                    and hashmap[position].nproc > 0
                    and hashmap[position].height == depth
                ):
                    return alpha, beta, score, True
                if hashmap[position].height >= depth:
                    if hashmap[position].flag == VALID:
                        score = hashmap[position].score
                        alpha = score
                        beta = score
                    elif (
                        hashmap[position].flag == UBOUND
                        and hashmap[position].score < beta
                    ):
                        score = hashmap[position].score
                        beta = hashmap[position].score
                    elif (
                        hashmap[position].flag == LBOUND
                        and hashmap[position].score > alpha
                    ):
                        score = hashmap[position].score
                        alpha = hashmap[position].score
                if hashmap[position].height == depth and alpha < beta:
                    hashmap[position].nproc += 1
            else:
                hashmap[position] = hashmap_data(
                    height=depth, flag=UNSET, nproc=1, score=0
                )
            return alpha, beta, score, False

    def __hashmap_store(self, position, alpha, beta, score, depth, hashmap):
        with self.lock:
            if position in hashmap:
                if hashmap[position].height > depth:
                    return
                elif hashmap[position].height == depth:
                    hashmap[position].nproc -= 1
                else:
                    hashmap[position].nproc = 0
            else:
                hashmap[position] = hashmap_data(
                    score=score, height=depth, nproc=0, flag=2
                )
            if score >= beta:
                hashmap[position].flag = LBOUND
            elif score <= alpha:
                hashmap[position].flag = UBOUND
            else:
                hashmap[position].flag = VALID
            hashmap[position].score = score
            hashmap[position].height = depth

    def __call__(self, position: Chess_Board) -> Any:
        with Pool(processes=self.n_threads) as pool:
            items = (
                [
                    (copy(position), self.depth, self._whole_hashmap)
                    for _ in range(self.n_threads)
                ],
            )

            processes = pool.starmap(
                self.__start_abdada,
                items,
                chunksize=10,
            )
            move_N_scores = [i for i in processes]

        print(move_N_scores)
        return move_N_scores[0]


def main():
    abdada_test = abdada(heuristic_function=nojus, depth=5, n_threads=12, debug=False)
    board = Chess_Board()
    while board.outcome() == 3:
        board.print_board()
        print(board.genmoves())
        board.move_san(input())

        board.print_board()
        print(evaluate_material(board))
        board.move(abdada_test(position=board)[1])
        print(evaluate_material(board))
        print()


if __name__ == "__main__":
    main()
