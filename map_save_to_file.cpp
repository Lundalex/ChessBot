#include <iostream>
#include <fstream>
#include <map>
#include <string>
#include "small_header.h"

// Define your custom struct

// Function to save map data to a binary file
void saveMapToBinaryFile(const map<string, hashmap_data> &myMap, const string &filename)
{
    // Open the file for writing in binary mode
    ofstream outputFile(filename, ios::binary);

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
        cout << "Data saved to file successfully.\n";
    }
    else
    {
        cerr << "Error opening file for writing.\n";
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
        cout << "Data loaded from file successfully.\n";
    }
    else
    {
        cerr << "Error opening file for reading.\n";
    }

    return loadedMap;
}

int main()
{
    // Your map
    map<string, hashmap_data> myMap;
    // Populate your map

    // Save the map data to a binary file
    saveMapToBinaryFile(myMap, "data.bin");

    // Load the map data from the binary file
    map<string, hashmap_data> loadedMap = loadMapFromBinaryFile("data.bin");

    // Now you can use loadedMap as needed

    return 0;
}

class some_test_class
{
private:
    map<string, hashmap_data> loadedMap = loadMapFromBinaryFile("data.bin");

public:
    map<string, hashmap_data> loadedMap = loadMapFromBinaryFile("data.bin");
    some_test_class(/* args */);
    ~some_test_class();
};

some_test_class::some_test_class(/* args */)
{
}

some_test_class::~some_test_class()
{
}
