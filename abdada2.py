from dataclasses import dataclass
from typing import Any
from board_test import AbdadaBoard as Chess_Board
from board_test import nojus, evaluate_material
import sys
from threading import Thread, Lock
from copy import deepcopy as copy
from random import randint

LBOUND = -1
UBOUND = 1
VALID = 0
UNSET = 2


class NewThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)

    def run(self):
        if self._target != None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


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
        self._hashmap = {}
        self.__heuristic_function = heuristic_function
        self.depth = depth
        self.lock = Lock()
        self.print_lock = Lock()
        self.debug = debug

    def __print(self, *args) -> None:
        with self.print_lock:
            if self.debug:
                print(*args)

    def __call__(self, position: Chess_Board) -> Any:
        threads = [
            NewThread(target=self.__start_abdada, args=(copy(position), self.depth))
            for _ in range(self.n_threads)
        ]
        for i in threads:
            i.start()

        move_N_scores = [i.join() for i in threads]
        print(move_N_scores)
        print([self._hashmap[i] for i in self._hashmap if self._hashmap[i].nproc < 0])
        return move_N_scores[0]

    def __start_abdada(self, position: Chess_Board, depth):
        a = randint(0, 69420)
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
                                    position.string(), alpha, beta, score, depth
                                )
                                self.__print(
                                    f"{list_of_done_moves}, {len(list_of_done_moves)} uno \n"
                                )
                                return score, move
                        # print(a, " ", j, " ", value, " ", score)
        self.__hashmap_store(position.string(), alpha, beta, score, depth)
        # print(move)
        self.__print(f"{list_of_done_moves}, {len(list_of_done_moves)} dos \n")
        return score, move

    def __abdada(self, position: Chess_Board, alpha, beta, depth, exclusive):
        # self.__print("hello")
        # self.__print(f"{position}, {depth}, {alpha}, {beta}, {exclusive} quatre")
        if position.outcome() != 3:
            # print(position.string())
            return alpha, beta, position.outcome() * 99999999, False
        elif depth == 0:
            # if abs(self.__heuristic_function(position)) == 1:
            #    print(position.string(), end="\n\n")
            return alpha, beta, -self.__heuristic_function(position), False
        score = float("-inf")
        alpha, beta, score, on_eval = self.__hashmap_retreive(
            position.string(), alpha, beta, depth, exclusive
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
                                    position.string(), alpha, beta, score, depth
                                )
                                return alpha, beta, -score, False
        self.__hashmap_store(position.string(), alpha, beta, score, depth)
        return alpha, beta, -score, False

    def __hashmap_retreive(self, position, alpha, beta, depth, exclusive):
        score = float("-inf")
        with self.lock:
            if position in self._hashmap:
                if (
                    exclusive
                    and self._hashmap[position].nproc > 0
                    and self._hashmap[position].height == depth
                ):
                    return alpha, beta, score, True
                if self._hashmap[position].height >= depth:
                    if self._hashmap[position].flag == VALID:
                        score = self._hashmap[position].score
                        alpha = score
                        beta = score
                    elif (
                        self._hashmap[position].flag == UBOUND
                        and self._hashmap[position].score < beta
                    ):
                        score = self._hashmap[position].score
                        beta = self._hashmap[position].score
                    elif (
                        self._hashmap[position].flag == LBOUND
                        and self._hashmap[position].score > alpha
                    ):
                        score = self._hashmap[position].score
                        alpha = self._hashmap[position].score
                if self._hashmap[position].height == depth and alpha < beta:
                    self._hashmap[position].nproc += 1

            else:
                self._hashmap[position] = hashmap_data(
                    height=depth, flag=UNSET, nproc=1, score=0
                )
            return alpha, beta, score, False

    def __hashmap_store(self, position, alpha, beta, score, depth):
        with self.lock:
            if position in self._hashmap:
                if self._hashmap[position].height > depth:
                    return
                elif self._hashmap[position].height == depth:
                    self._hashmap[position].nproc -= 1
                else:
                    self._hashmap[position].nproc = 0
            else:
                self._hashmap[position] = hashmap_data(
                    score=score, height=depth, nproc=0, flag=2
                )
            if score >= beta:
                self._hashmap[position].flag = LBOUND
            elif score <= alpha:
                self._hashmap[position].flag = UBOUND
            else:
                self._hashmap[position].flag = VALID
            self._hashmap[position].score = score
            self._hashmap[position].height = depth


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


# us the c++ file as refrence to understand the python code, it's alot cleaner and has proper comments
if __name__ == "__main__":
    main()
