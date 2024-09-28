from socket import *
import threading
import ast

clientes = {}


def processa_comando(comando, nickname, client_address, server_socket, request):
    def broadcast(msg, sender_address):
        for client, addr in clientes.items():
            if addr != sender_address:
                server_socket.sendto(msg.encode(), addr)

    def armazena_cliente(nickname, client_address):
        if nickname is not None and nickname not in clientes:
            clientes[nickname] = client_address
            return True
        return False

    if nickname is None:
        server_socket.sendto(
            "Para enviar mensagens, você precisa se registrar".encode(), client_address)
        return

    if comando.startswith("/reg"):
        if armazena_cliente(nickname, client_address) is True:
            server_socket.sendto(
                "Você foi registrado com sucesso!".encode(), client_address)
            print(f"Cliente {nickname} registrado!")
        else:
            server_socket.sendto(
                "Este nickname já está em uso".encode(), client_address)
    elif comando.startswith("/msg") and not "-n" in comando:
        msg = comando.split("/msg ")[1]
        msg = f"{nickname}: {msg}"

        broadcast(msg, client_address)
        print(f"Mensagem: \"{msg}\"")
    elif comando.startswith("/msg") and "-n" in comando:
        msg = comando.split("/msg -n ")[1]
        destino = msg.split(" ")[0]
        msg_text = comando.split(f"/msg -n {destino} ")[1]
        msg = f"{nickname}: {msg_text}"

        if destino in clientes:
            print(f"Mensagem para {destino}: \"{msg}\"")
            server_socket.sendto(msg.encode(), clientes[destino])
        else:
            server_socket.sendto(
                f"Cliente {destino} não encontrado".encode(), client_address)
    elif comando.startswith("/file") and "-n" in comando:
        destino = comando.split(" ")[2]
        filename = comando.split(" ")[3]
        data = {
            "data": request["data"],
            "from": nickname,
            "filename": filename
        }
        if destino in clientes:
            print(f"Arquivo \"{filename}\" enviado para {destino}")
            server_socket.sendto(
                f"FILE: {str(data)}".encode(), clientes[destino])
        else:
            server_socket.sendto(
                f"Cliente {destino} não encontrado".encode(), client_address)
    else:
        server_socket.sendto("Comando inválido".encode(), client_address)


def inicia_servidor(host="localhost", port=40000):
    server_socket = socket(AF_INET, SOCK_DGRAM)  # Create a UDP socket
    server_socket.bind((host, port))

    print(f"Servidor está ativo 🚀 em {host}:{port}")

    while True:
        try:
            request, client_address = server_socket.recvfrom(1024)

            if not request:
                continue

            request = ast.literal_eval(request.decode())
            nickname = request["nickname"]
            comando = request["comando"]

            processa_comando(comando, nickname, client_address,
                             server_socket, request)
        except Exception as e:
            print("[ERRO] Exceção ocorrida")
            print(e)
            continue


if __name__ == "__main__":
    inicia_servidor()
