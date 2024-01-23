#include <iostream>
#include <map>
#include <string>
using namespace std;

struct chess_move
{
    string blank;
};

class ChessBoard
{
public:
    string stringify()
    {
        return "testing";
    }
    int outcome()
    {
        return 3;
    };
    void move(chess_move Cmove)
    {
    }
    void unmove()
    {
    }

    tuple<chess_move *, int> gen_moves()
    {
        chess_move some_arr[3] = {};
        chess_move *return_val = &some_arr[0];
        return {return_val, size(some_arr)};
    };
};
