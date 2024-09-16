from socket import *

server_port = 12000
server_host = 'localhost'
client_socket = socket(AF_INET, SOCK_DGRAM)

message = input("Enter a message: ")

client_socket.sendto(message.encode(), (server_host, server_port))

updated_message, server_address = client_socket.recvfrom(2048)
print(updated_message.decode())

client_socket.close()