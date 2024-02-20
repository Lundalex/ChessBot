#include <string>
#include <mutex>
#include <tuple>
#include <thread>
#include "ChessBoard.cpp"
#include <iostream>
#include <fstream>
// #include "network_com.cpp"
// #include "map_save_to_file.cpp"
//   #include "thc-chess-library/src/thc.h"
#include <csignal>
#include <cmath>
#include <cstdlib>
#include "small_header.h"

using namespace std;

void saveMapToBinaryFile(const map<string, hashmap_data> &myMap, const string &filename)
{
    // Open the file for writing in binary mode
    ofstream outputFile(filename, ios::binary | ios::trunc);

    if (outputFile.is_open())
    {
        // Iterate over the map and write each key-value pair to the file
        for (const auto &pair : myMap)
        {
            // Write the key's length and the key itself
            size_t keySize = pair.first.size();
            outputFile.write(reinterpret_cast<const char *>(&keySize), sizeof(keySize));
            outputFile.write(pair.first.data(), keySize);

            // Write the custom struct
            outputFile.write(reinterpret_cast<const char *>(&pair.second), sizeof(hashmap_data));
        }
        outputFile.close();
        // cout << "Data saved to file successfully.\n";
    }
    else
    {
        cerr << "Error opening file: " << filename
             << std::endl;

        // Check for specific error conditions
        if (outputFile.bad())
        {
            cerr << "Fatal error: badbit is set." << endl;
        }

        if (outputFile.fail())
        {
            // Print a more detailed error message using
            // strerror
            cerr << "Error details: " << strerror(errno)
                 << endl;
        }

        // Handle the error or exit the program
    }
}

// Function to load map data from a binary file
map<string, hashmap_data> loadMapFromBinaryFile(const string &filename)
{
    map<string, hashmap_data> loadedMap;

    // Open the file for reading in binary mode
    ifstream inputFile(filename, ios::binary);

    if (inputFile.is_open())
    {
        // Read data from the file and populate the map
        while (inputFile.good())
        {
            // Read the key's length
            size_t keySize;
            inputFile.read(reinterpret_cast<char *>(&keySize), sizeof(keySize));
            if (!inputFile.good())
                break; // Break if failed to read keySize

            // Read the key
            string key;
            key.resize(keySize);
            inputFile.read(&key[0], keySize);

            // Read the custom struct
            hashmap_data value;
            inputFile.read(reinterpret_cast<char *>(&value), sizeof(hashmap_data));

            // Insert into the map
            loadedMap[key] = value;
        }
        inputFile.close();
        // cout << "Data loaded from file successfully.\n";
    }
    else
    {
        cerr << "Error opening file for reading.\n";
    }

    return loadedMap;
}

class abdada
{
public:
    int n_threads;
    int depth;
    float (*heuristics)(ChessBoard); // pointer to heurisitcs function
    bool debug;                      // wheter to turn on or off debug mode , default is off
    string FileToSave;

private:
    mutex lock;                                     // thread lock
    mutex print_lock;                               // thead lock for printing
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
            // cout << (*Phashmap)[position].nproc << " " << (*Phashmap)[position].depth << " " << (*Phashmap)[position].flag << " " << (*Phashmap)[position].score << "\n";
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
            }
            if ((alpha < beta) && ((*Phashmap)[position].depth == depth)) // incriment the number of current threads searching the node.
                (*Phashmap)[position].nproc++;
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

    pair<float, bool> InnerAbdada(ChessBoard position, float alpha, float beta, int depth, bool exclusive)
    {
        // // cout << "edfjgbdsacd\n";
        if (!(position.outcome() == 3))
        { // return the terminal value , a very big terminal value, just no infinity, depening on winning player
            // // cout << "exit 1 : " << -position.outcome() * 9999999999999999 << "\n";

            return {-position.outcome() * 9999999999999999, false};
        }
        if (depth == 0)
        {
            return {-(*heuristics)(position), false};
        }
        float score = -INFINITY; // just get the worst possible baseline so all other moves are better
        bool on_eval;
        tie(score, alpha, beta, on_eval) = HashMapRetrieve(position.stringify(), alpha, beta, depth, exclusive); // basically just a stright copy from the wiki, don't ask me why or how, it is what it is
        vector<chess_move> moves;
        moves = position.gen_moves();

        if (on_eval)
        { // return if anothre node is evalutaing the current pos and the node is in exclusice mode
            // // cout << "exit 3\n";
            return {score, true};
        }
        if (alpha >= beta)
        { // if the node is pruned
            // // cout << "exit 4" << alpha << " " << beta << " \n";
            return {-score, false};
        }
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
                    // print_lock.lock();
                    //  // cout << Cmove.src << " : " << Cmove.dst << " :\n";
                    // print_lock.unlock();
                    if (alpha < beta)
                    {
                        sub_exclusive = ((i == 0) && (j != 0));                                             // is in exclusive mode if ,and only if, both the searched node ISN'T the first node being evaluted (this is to get a good alpha/beta) and is on the first pass through
                        position.move(Cmove);                                                               // do the move
                        value = InnerAbdada(position, -beta, -max(alpha, score), depth - 1, sub_exclusive); // searched the resulting move
                        position.unmove();                                                                  //
                        // // cout << Cmove.dst << ";:;:;:\n";                                  // undo the move
                        if (std::get<1>(value)) // check id the node is under eval
                            alldone = false;
                        else if (std::get<0>(value) * 0.999 > score)
                        {
                            score = std::get<0>(value) * 0.999; // save the score if it's better than a prevoius score
                            if (!(score < beta))
                            {

                                HashMapStore(position.stringify(), alpha, beta, score, depth);
                                // m// cout << "exit 5\n";
                                return {-score, false}; // if the current node is pruned , save the score and exit
                            }
                        }
                    }
                }
            }
        }
        HashMapStore(position.stringify(), alpha, beta, score, depth); // save after all subnodes are searched
        // // cout << "exit 6\n";
        return {-score, false};
    };

    void StartAbdada(ChessBoard position, int depth, pair<float, chess_move> *return_pointer) // basically abdada, but with a lot less ifs and it returns the score and move
    {
        // // cout << "I've started\n";
        float score = -INFINITY; // just get the worst possible baseline so all other moves are better
        bool on_eval;
        float alpha = -INFINITY;
        float beta = INFINITY;
        // // cout << alpha << " is it good?-\n";
        // // cout << beta << " is it good.-\n";
        // // cout << (alpha < beta) << " is it good!-\n";
        bool exclusive = false;
        // tie(score, alpha, beta, on_eval) = HashMapRetrieve(position.stringify(), alpha, beta, depth, exclusive); // basically just a stright copy from the wiki, don't ask me why or how, it is what it is
        // cout << alpha << " : " << beta << " ;\n";
        vector<chess_move> moves;
        moves = position.gen_moves();
        bool alldone = false;
        bool sub_exclusive;
        pair<float, bool> value;
        chess_move best_move;

        for (int i = 0; i < 2; i++)
        {
            // // cout << alpha << " is it good?\n";
            // // cout << beta << " is it good.\n";
            // // cout << (alpha < beta) << " is it good!\n";
            if ((alpha < beta) && !alldone)
            {
                alldone = true;
                // // cout << moves.size() << " cray cray\n";
                for (int j = 0; j < moves.size(); j++)
                {
                    chess_move Cmove = moves[j];
                    // // cout << Cmove.src << " : " << Cmove.dst << " before\n";
                    if (alpha < beta)
                    {
                        sub_exclusive = ((i == 0) && (j != 0));
                        position.move(Cmove);
                        print_lock.lock();
                        // // cout << Cmove.dst << " ; " << Cmove.src << " ; ";
                        print_lock.unlock();
                        // // cout << "edfjgbdsacd";
                        value = InnerAbdada(position, -beta, -max(alpha, score), depth - 1, sub_exclusive);
                        position.unmove();
                        // // cout << std::get<0>(value) << " " << score << " " << (std::get<0>(value) > score) << "\n";
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
                                *return_pointer = make_pair(score, best_move);
                                return;
                            }
                        }
                    }
                    // // cout << Cmove.src << " : " << Cmove.dst << " after\n";
                }
            }
        }
        HashMapStore(position.stringify(), alpha, beta, score, depth);
        // // cout << best_move.src << " : " << best_move.dst << ";\n";
        // // cout << (std::get<1>(*return_pointer)).src << " : " << (std::get<1>(*return_pointer)).dst << "|\n";
        *return_pointer = make_pair(score, best_move);
        // // cout << (std::get<1>(*return_pointer)).src << " : " << (std::get<1>(*return_pointer)).dst << "|-\n";

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

        chess_move r_move = std::get<1>(some_func_return[0]);
        // cout << r_move.src << " : " << r_move.dst << "|\n";
        delete[] ThreadList;
        delete[] some_func_return;
        return r_move; // return the best move
    };
    abdada(int n_threads, int depth, float (*heuristics)(ChessBoard), string FileToSave, bool debug = false) : n_threads(n_threads), depth(depth), heuristics(heuristics), debug(debug), FileToSave(FileToSave)
    {

        hashmap = loadMapFromBinaryFile(FileToSave);
    };
    ~abdada()
    {
        // cout << hashmap.size() << "\n";
        // cout << FileToSave << "\n";
        saveMapToBinaryFile(hashmap, FileToSave);
    }
};

int not_main()
{
    int n_threads, depth;
    ChessBoard TheBoard;
    cin >> n_threads;
    cin >> depth;
    float (*heuristics_func)(ChessBoard);
    heuristics_func = &nojus;
    abdada the_AI(n_threads, depth, heuristics_func, "saveddata.dat");
    string Uin;
    while (TheBoard.outcome() == 3)
    {
        TheBoard.move(the_AI.search(TheBoard));
        // cout << TheBoard.old_moves[0].src << " " << TheBoard.old_moves[0].dst << "smthssss";
        TheBoard.display_position("an interesting position");
        // cout << nojus(TheBoard) << "\n";
        cin >> Uin;
        TheBoard.user_move(Uin);
        TheBoard.display_position("a less interesting position");
    }
    // // // cout << TheBoard.true_outcome();
    return 0;
};

abdada *the_AI;

void exiting(int num)
{
    delete the_AI;
    cout << "HEJ DÅ";
}

int main()
{
    signal(SIGINT, exiting);  // Interrupt (Ctrl+C)
    signal(SIGTERM, exiting); // Termination signal
    int n_threads, depth;
    ChessBoard TheBoard;
    n_threads = 12;
    // cin >> depth;
    depth = 6;
    float (*heuristics_func)(ChessBoard);
    heuristics_func = &nojus;
    the_AI = new abdada(n_threads, depth, heuristics_func, "saveddata.dat");
    string Uin;
    chess_move the_move;

    while (TheBoard.outcome() == 3)
    {
        the_move = (*the_AI).search(TheBoard);
        TheBoard.move(the_move);
        // TheBoard.display_position("an interesting position");
        cout << the_move.src << "," << the_move.dst << "\n";
        cin >> Uin;
        TheBoard.user_move(Uin);
        // TheBoard.display_position("an interesting position");
    }

    delete the_AI;
    // cout << TheBoard.true_outcome();
    return 0;
}
