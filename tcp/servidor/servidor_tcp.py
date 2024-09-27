from socket import *
import threading
import ast

clientes = {}


def processa_cliente(client_socket):
    def broadcast(msg, sender):
        for client in clientes:
            if client != sender:
                client_socket = clientes[client]
                client_socket.send(msg.encode())

    def armazena_cliente(nickname, socket):
        if nickname is not None and nickname not in clientes:
            clientes[nickname] = socket
            return True
        return False

    def processa_comando(comando, nickname):
        if nickname is None:
            client_socket.send(
                "Para enviar mensagens, você precisa se registrar".encode())
            return

        if comando.startswith("/reg"):
            if armazena_cliente(nickname, client_socket) is True:
                client_socket.send("Você foi registrado com sucesso!".encode())
                print(f"Cliente {nickname} registrado!")
            else:
                client_socket.send("Este nickname já está em uso".encode())
        elif comando.startswith("/msg") and not "-n" in comando:
            msg = comando.split("/msg ")[1]
            msg = f"{nickname}: {msg}"

            broadcast(msg, nickname)
            print(f"Mensagem: \"{msg}\"")
        elif comando.startswith("/msg") and "-n" in comando:
            msg = comando.split("/msg -n ")[1]
            destino = msg.split(" ")[0]
            msg = f"{nickname}: {msg.split(destino)[1]}"

            if destino in clientes:
                print(f"Mensagem para {destino}: \"{msg}\"")
                clientes[destino].send(msg.encode())
            else:
                client_socket.send(
                    f"Cliente {destino} não encontrado".encode())
        else:
            client_socket.send("Comando inválido".encode())

    while True:
        try:
            request = client_socket.recv(1024).decode()

            if not request:
                break

            request = ast.literal_eval(request)

            nickname = request["nickname"]
            comando = request["comando"]

            processa_comando(comando, nickname)
        except Exception as e:
            print("[ERRO] Exeção ocorrida")
            print(e)
            continue


def inicia_servidor(host="localhost", port=40000):
    server = socket(AF_INET, SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    print(f"Servidor está ativo 🚀 em {host}:{port}")

    while True:
        client_socket, addr = server.accept()

        thread = threading.Thread(
            target=processa_cliente, args=(client_socket,))
        thread.start()


if __name__ == "__main__":
    inicia_servidor()
