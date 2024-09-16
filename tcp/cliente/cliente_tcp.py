from socket import *

server_host = '127.0.0.1'
server_port = 45000

nickname = None

while True:
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    comando = input("Digite um comando: ")

    if nickname is None and comando.startswith("/reg"):
        nickname = comando.split(" ")[1]

    comando = {
        "comando": comando,
        "nickname": nickname
    }

    client_socket.send(str(comando).encode())

    resposta = client_socket.recv(1024).decode()
    print(f"Resposta do servidor: {resposta}")

    client_socket.close()