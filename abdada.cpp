#include <iostream>
#include <map>
#include <string>
#include <mutex>
#include <tuple>
#include <thread>
#include "ChessBoard.cpp"
#include <cmath>

using namespace std;

struct hashmap_data // struct to store data in the hashmap
{
    float score;
    int depth;
    int nproc;
    int flag;
};

class abdada
{
public:
    int n_threads;
    int depth;
    float (*heuristics)(ChessBoard); // pointer to heurisitcs function
    bool debug;                      // wheter to turn on or off debug mode , default is off
    abdada(int n_threads, int depth, float (*heuristics)(ChessBoard), bool debug = false) : n_threads(n_threads), depth(depth), heuristics(heuristics), debug(debug){};

private:
    mutex lock;                                     // thread lock
    map<string, hashmap_data> hashmap;              // class hashmap
    map<string, hashmap_data> *Phashmap = &hashmap; // refrence to hashmap so threads can access it

    int LBOUND = -1;
    int UBOUND = 1;
    int VALID = 0;
    int UNSET = 2; // some globals for easier later assigment , could possibly into the class later , now moved to class

    tuple<float, float, float, bool> HashMapRetrieve(string position, float alpha, float beta, int depth, bool exclusive) // function to retrieve data from teh hashmap
    {
        float score = -INFINITY;

        lock.lock(); // lock so only one thread can use it at any one time , probably should make this function concurrent as it basically IO bound

        if ((*Phashmap).count(position)) // the amount of values that has the key of the current position in the hashmap at the memory adress Phashmap
        {
            if (exclusive && ((*Phashmap)[position].nproc > 0) && ((*Phashmap)[position].depth == depth)) // if the node is meant to run in exclusive mode and there are others threads evaluating the node at the same depth then return ON_EVAL
            {
                lock.unlock();                               // unlock the thread
                return make_tuple(score, alpha, beta, true); // exit on eval
            }
            if (!((*Phashmap)[position].depth < depth)) // if the stored hashmap is at the same or greater depth than the current evaluation then return the stored values
            {
                if ((*Phashmap)[position].flag == VALID) // if the nodes was fully searched
                {
                    score = (*Phashmap)[position].score;
                    alpha = score;
                    beta = score;
                }
                else if (((*Phashmap)[position].flag == UBOUND) && ((*Phashmap)[position].score < beta)) // if the Lower, yes LOWER bound was hit, it seems quite confusing but is logical when you think about it
                {
                    score = (*Phashmap)[position].score;
                    beta = score;
                }
                else if (((*Phashmap)[position].flag == LBOUND) && ((*Phashmap)[position].score > alpha)) // if the upper bound was hit
                {
                    score = (*Phashmap)[position].score;
                    alpha = score;
                }
                if ((alpha < beta) && ((*Phashmap)[position].depth == depth)) // incriment the number of current threads searching the node.
                    (*Phashmap)[position].nproc++;
            }
        }
        else
        {
            (*Phashmap)[position].flag = UNSET; // if its the first thread to evaluate the node then store that
            (*Phashmap)[position].depth = depth;
            (*Phashmap)[position].nproc = 1;
        }
        lock.unlock(); // unlock and return the data
        return make_tuple(score, alpha, beta, false);
    }

    void HashMapStore(string position, float alpha, float beta, float score, int depth)
    {
        lock.lock();                     // lock the so only on thread can access
        if ((*Phashmap).count(position)) // if the position exists
        {
            if ((*Phashmap)[position].depth > depth) // if the stored position is of greater depth than the given position
            {
                lock.unlock(); // unlock and exit
                return;
            }
            else if ((*Phashmap)[position].depth == depth) // if the depths are equal
                (*Phashmap)[position].nproc--;             // decriment the number of processors evaluating the node
            else
                (*Phashmap)[position].nproc = 0; // otherwise set to zero
        }
        else // if it doesn't exist set nproc to zero
            (*Phashmap)[position].nproc = 0;
        if (!(score < beta))                     // if the higher bound was reached then set the flag to lower bound, yes LOWER BOUND
            (*Phashmap)[position].flag = LBOUND; //
        else if (!(score > alpha))               // if it reaches the lower bound then set the flag to high bound
            (*Phashmap)[position].flag = UBOUND; //
        else                                     // else set it to valid
            (*Phashmap)[position].flag = VALID;
        (*Phashmap)[position].score = score; // store and exit
        (*Phashmap)[position].depth = depth;

        lock.unlock();
        return;
    };

    pair<float, bool> InnerAbdada(ChessBoard position, int alpha, int beta, int depth, bool exclusive)
    {
        if (!(position.outcome() == 3)) // return the terminal value , a very big terminal value, just no infinity, depening on winning player
            return {position.outcome() * 9999999999999999, false};
        if (depth == 0)
            return {(*heuristics)(position), false};
        float score = -INFINITY; // just get the worst possible baseline so all other moves are better
        bool on_eval;
        tie(alpha, beta, score, on_eval) = HashMapRetrieve(position.stringify(), alpha, beta, depth, exclusive); // basically just a stright copy from the wiki, don't ask me why or how, it is what it is
        vector<chess_move> moves;
        moves = position.gen_moves();

        if (on_eval) // return if anothre node is evalutaing the current pos and the node is in exclusice mode
            return {score, true};
        if (!(alpha < beta)) // if the node is pruned
            return {score, false};
        bool alldone = false;
        bool sub_exclusive;
        pair<float, bool> value;    // the evaluted nodes value
        for (int i = 0; i < 2; i++) // iterating twice over the same list so that any node already under eval gets evald only after nodes not on eval are searched
        {
            if ((alpha < beta) && !alldone)
            {
                alldone = true;
                for (int j = 0; j < moves.size(); j++) // iterating over all moves
                {
                    chess_move Cmove = moves[j]; // current move
                    if (alpha < beta)
                    {
                        sub_exclusive = ((i == 0) && (j != 0));                           // is in exclusive mode if ,and only if, both the searched node ISN'T the first node being evaluted (this is to get a good alpha/beta) and is on the first pass through
                        position.move(Cmove);                                             // do the move
                        value = InnerAbdada(position, alpha, beta, depth, sub_exclusive); // searched the resulting move
                        position.unmove();                                                // undo the move
                        if (std::get<1>(value))                                           // check id the node is under eval
                            alldone = false;
                        else if (std::get<0>(value) > score)
                        {
                            score = std::get<0>(value); // save the score if it's better than a prevoius score
                            if (!(score < beta))
                            {
                                HashMapStore(position.stringify(), alpha, beta, score, depth);
                                return {-score, false}; // if the current node is pruned , save the score and exit
                            }
                        }
                    }
                }
            }
        }
        HashMapStore(position.stringify(), alpha, beta, score, depth); // save after all subnodes are searched
        return {-score, false};
    };

    void StartAbdada(ChessBoard position, int depth, pair<float, chess_move> *return_pointer) // basically abdada, but with a lot less ifs and it returns the score and move
    {
        float score = -INFINITY; // just get the worst possible baseline so all other moves are better
        bool on_eval;
        float alpha = -INFINITY;
        float beta = INFINITY;
        bool exclusive = false;
        tie(alpha, beta, score, on_eval) = HashMapRetrieve(position.stringify(), alpha, beta, depth, exclusive); // basically just a stright copy from the wiki, don't ask me why or how, it is what it is
        vector<chess_move> moves;
        moves = position.gen_moves();
        bool alldone = false;
        bool sub_exclusive;
        pair<float, bool> value;
        chess_move best_move;
        for (int i = 0; i < 2; i++)
        {
            if ((alpha < beta) && !alldone)
            {
                alldone = true;
                for (int j = 0; j < moves.size(); j++)
                {
                    chess_move Cmove = moves[j];
                    if (alpha < beta)
                    {
                        sub_exclusive = ((i == 0) && (j != 0));
                        position.move(Cmove);
                        value = InnerAbdada(position, alpha, beta, depth, sub_exclusive);
                        position.unmove();
                        if (std::get<1>(value))
                        {
                            alldone = false;
                        }
                        else if (std::get<0>(value) > score)
                        {
                            score = std::get<0>(value);
                            best_move = Cmove;
                            if (!(score < beta))
                            {
                                HashMapStore(position.stringify(), alpha, beta, score, depth);
                                *return_pointer = {score, best_move};
                                return;
                            }
                        }
                    }
                }
            }
        }
        HashMapStore(position.stringify(), alpha, beta, score, depth);
        *return_pointer = {score, best_move};
        return;
    };
    // Starting script for the abdada algorithm
public:
    chess_move search(ChessBoard position)
    {
        pair<float, chess_move> *some_func_return = new pair<float, chess_move>[n_threads]; // function return
        thread *ThreadList = new thread[n_threads];                                         // a list of threads

        for (int i = 0; i < n_threads; i++)
        {
            ThreadList[i] = thread([this](auto arg1, auto arg2, auto arg3)
                                   { this->StartAbdada(arg1, arg2, arg3); },
                                   ChessBoard(position), depth, &(some_func_return[i])); // start the threads
        }
        for (int i = 0; i < n_threads; i++)
        {
            ThreadList[i].join(); // join the threads
        }
        delete[] ThreadList;
        delete[] some_func_return;
        return std::get<1>(some_func_return[0]); // return the best move
    };
};

int main()
{
    int n_threads, depth;
    ChessBoard TheBoard;
    cin >> n_threads;
    cin >> depth;
    float (*heuristics_func)(ChessBoard);
    heuristics_func = &nojus;
    abdada the_AI(n_threads, depth, heuristics_func);
    string Uin;
    while (TheBoard.outcome() == 3)
    {
        TheBoard.move(the_AI.search(TheBoard));
        TheBoard.display_position("an interesting position");

        cin >> Uin;
        TheBoard.user_move(Uin);
        TheBoard.display_position("a less interesting position");
    }
    cout << TheBoard.true_outcome();
    return 0;
};