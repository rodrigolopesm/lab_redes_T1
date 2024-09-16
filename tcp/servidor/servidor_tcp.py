from socket import *
import ast

clientes = {}

def proessa_comando(comando):
    return "Comando recebido"

def armazena_cliente(nickname, addr):
    if nickname not in clientes:
        clientes[nickname] = addr
        print(f"Cliente {nickname} armazenado")


server_port = 45000
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('', server_port))
server_socket.listen(1)

print("Server is on 🚀")

while True:
    connection_socket, addr = server_socket.accept()

    request = connection_socket.recv(1024).decode()
    request = ast.literal_eval(request)

    nickname = request["nickname"]
    comando = request["comando"]

    armazena_cliente(nickname, addr)

    resposta = proessa_comando(comando)

    connection_socket.send(resposta.encode())
    connection_socket.close()
