#include <fstream>
#include "small_header.h"
// Define the struct

// Serialization functions for hashmap_data struct
void serialize(std::ofstream &file, const hashmap_data &data)
{
    file.write(reinterpret_cast<const char *>(&data), sizeof(data));
}

void deserialize(std::ifstream &file, hashmap_data &data)
{
    file.read(reinterpret_cast<char *>(&data), sizeof(data));
}

// Function to save the map to file
void saveMapToFile(const std::map<std::string, hashmap_data> &myMap, const std::string &filename)
{
    std::ofstream file(filename, std::ios::binary);
    if (file.is_open())
    {
        for (const auto &pair : myMap)
        {
            // Write the key size and key data
            size_t keySize = pair.first.size();
            file.write(reinterpret_cast<const char *>(&keySize), sizeof(keySize));
            file.write(pair.first.data(), keySize);

            // Serialize the value
            serialize(file, pair.second);
        }
        file.close();
        std::cout << "Map saved to file: " << filename << std::endl;
    }
    else
    {
        std::cerr << "Unable to open file for writing: " << filename << std::endl;
    }
}

// Function to load the map from file
MapType loadMapFromFile(const std::string &filename)
{
    MapType myMap;
    std::ifstream file(filename, std::ios::binary);
    if (file.is_open())
    {
        while (!file.eof())
        {
            // Read key size
            size_t keySize;
            file.read(reinterpret_cast<char *>(&keySize), sizeof(keySize));
            if (file.eof())
                break;

            // Read key
            std::string key;
            key.resize(keySize);
            file.read(&key[0], keySize);

            // Deserialize the value
            hashmap_data value;
            deserialize(file, value);

            // Insert into map
            myMap[key] = value;
        }
        file.close();
        std::cout << "Map loaded from file: " << filename << std::endl;
    }
    else
    {
        std::cout << "Unable to open file for reading: " << filename << std::endl;
    }
    return myMap;
}