#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "Ws2_32.lib")

namespace MyNetwork
{
    SOCKET server_socket;

    void start_server(int port)
    {
        WSADATA wsaData;
        struct sockaddr_in server_address;

        // Initialize Winsock
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
        {
            std::cerr << "WSAStartup failed\n";
            exit(EXIT_FAILURE);
        }

        // Create socket
        if ((server_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) == INVALID_SOCKET)
        {
            std::cerr << "Socket creation failed\n";
            WSACleanup();
            exit(EXIT_FAILURE);
        }

        server_address.sin_family = AF_INET;
        server_address.sin_addr.s_addr = INADDR_ANY;
        server_address.sin_port = htons(port);

        // Bind socket
        if (bind(server_socket, (struct sockaddr *)&server_address, sizeof(server_address)) == SOCKET_ERROR)
        {
            std::cerr << "Bind failed\n";
            closesocket(server_socket);
            WSACleanup();
            exit(EXIT_FAILURE);
        }

        // Listen
        if (listen(server_socket, SOMAXCONN) == SOCKET_ERROR)
        {
            std::cerr << "Listen failed\n";
            closesocket(server_socket);
            WSACleanup();
            exit(EXIT_FAILURE);
        }
    }

    void close_connection()
    {
        closesocket(server_socket);
        WSACleanup();
    }

    void send_data(const char *data, int length)
    {
        send(server_socket, data, length, 0);
    }

    std::string receive_data()
    {
        char buffer[1024] = {0};
        int bytes_received = recv(server_socket, buffer, 1024, 0);
        if (bytes_received == SOCKET_ERROR)
        {
            std::cerr << "Receive failed\n";
            close_connection();
            exit(EXIT_FAILURE);
        }
        return std::string(buffer);
    }
} // namespace MyNetwork
