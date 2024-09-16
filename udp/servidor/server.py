from socket import *

server_port = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('', server_port))

print("Server is on 🚀")

while True:
    message, client_address = server_socket.recvfrom(2048)

    print(f"Received message from {client_address}")

    modified_message = message.decode().upper()

    print(f"Modified message: {modified_message}")

    server_socket.sendto(modified_message.encode(), client_address)