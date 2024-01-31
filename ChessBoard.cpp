#include <iostream>
#include <map>
#include <string>
#include "thc-chess-library/src/thc.h"
// #include "thc-chess-library/src/thc.cpp"
using namespace std;

typedef thc::Move chess_move;

class ChessBoard
{
public:
    ChessBoard(){};
    ChessBoard(const ChessBoard &src)
    {
        actual_board = thc::ChessRules(src.actual_board);
        old_moves = src.old_moves;
    };

    vector<thc::Move> old_moves;
    thc::ChessRules actual_board;
    void display_position(const std::string &description)
    {

        thc::ChessRules &cr = actual_board;
        std::string fen = cr.ForsythPublish();
        std::string s = cr.ToDebugStr();
        printf("%s\n", description.c_str());
        printf("FEN (Forsyth Edwards Notation) = %s\n", fen.c_str());
        printf("Position = %s\n", s.c_str());
    }

    string stringify()
    {
        string return_str = actual_board.ForsythPublish();
        return_str.resize(return_str.rfind(' '));
        return_str.resize(return_str.rfind(' '));
        return return_str;
    }
    int outcome()
    {
        thc::TERMINAL eval_temp;
        actual_board.Evaluate(eval_temp);

        if ((eval_temp == 1) || (eval_temp == -1))
            return -1;
        else if ((eval_temp == 2) || (eval_temp == -2))
            return 0;
        else
            return 3;
    };
    int true_outcome()
    {
        thc::TERMINAL eval_temp;
        actual_board.Evaluate(eval_temp);
        return eval_temp;
    };

    void user_move(string str)
    {
        thc::Move mv;
        mv.TerseIn(&actual_board, &(str[0]));
        actual_board.PlayMove(mv);
    }
    void move(chess_move Cmove)
    {
        actual_board.PushMove(Cmove);
        old_moves.push_back(Cmove);
    }
    void unmove()
    {

        actual_board.PopMove(old_moves[old_moves.size()]);
        old_moves.pop_back();
    }

    vector<chess_move> gen_moves()
    {
        std::vector<thc::Move> moves;
        actual_board.GenLegalMoveList(moves);
        return moves;
    };
};

int piece_score(char some_square)
{
    switch (some_square)
    {
    case 'P':
        return 1;
        break;
    case 'p':
        return -1;
        break;
    case 'B':
        return 3;
        break;
    case 'b':
        return -3;
        break;
    case 'N':
        return 3;
        break;
    case 'n':
        return -3;
        break;
    case 'R':
        return 5;
        break;
    case 'r':
        return -5;
        break;
    case 'Q':
        return 9;
        break;
    case 'q':
        return -9;
        break;
    default:
        return 0;
        break;
    }
};

float nojus(ChessBoard position)
{
    int return_score;
    for (int i; i < 64; i++)
    {
        return_score = return_score + piece_score(position.actual_board.squares[i]);
    }
    return return_score;
};