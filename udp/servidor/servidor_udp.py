from socket import *
import threading
import ast

# Dicionário para armazenar clientes, onde a chave é o nickname e o valor é o endereço.
clientes = {}

# Função que processa os comandos recebidos dos clientes


def processa_comando(comando, nickname, client_address, server_socket, request):
    # Função para enviar uma mensagem para todos os clientes, exceto o remetente
    def broadcast(msg, sender_address):
        for client, addr in clientes.items():
            if addr != sender_address:  # Garante que o remetente não receba sua própria mensagem
                # Envia a mensagem para o cliente
                server_socket.sendto(msg.encode(), addr)

    # Função para armazenar o cliente se o nickname ainda não foi registrado
    def armazena_cliente(nickname, client_address):
        if nickname is not None and nickname not in clientes:
            # Adiciona o cliente no dicionário
            clientes[nickname] = client_address
            return True
        return False

    # Se o cliente ainda não estiver registrado, ele não pode enviar mensagens
    if nickname is None:
        server_socket.sendto(
            "Para enviar mensagens, você precisa se registrar".encode(), client_address)
        return

    # Comando para registrar o cliente
    if comando.startswith("/reg"):
        if armazena_cliente(nickname, client_address):
            server_socket.sendto(
                "Você foi registrado com sucesso!".encode(), client_address)
            print(f"Cliente {nickname} registrado!")
        else:
            server_socket.sendto(
                "Este nickname já está em uso".encode(), client_address)

    # Comando para enviar mensagem pública a todos os clientes
    elif comando.startswith("/msg") and "-n" not in comando:
        msg = comando.split("/msg ")[1]
        msg = f"{nickname}: {msg}"

        broadcast(msg, client_address)  # Envia a mensagem a todos os clientes
        print(f"Mensagem: \"{msg}\"")

    # Comando para enviar mensagem privada para um cliente específico
    elif comando.startswith("/msg") and "-n" in comando:
        msg = comando.split("/msg -n ")[1]
        destino = msg.split(" ")[0]  # Obtém o destinatário
        msg_text = comando.split(f"/msg -n {destino} ")[1]  # Obtém a mensagem
        msg = f"{nickname}: {msg_text}"

        if destino in clientes:
            print(f"Mensagem para {destino}: \"{msg}\"")
            # Envia a mensagem ao destinatário
            server_socket.sendto(msg.encode(), clientes[destino])
        else:
            server_socket.sendto(
                f"Cliente {destino} não encontrado".encode(), client_address)

    # Comando para enviar um arquivo para um cliente específico
    elif comando.startswith("/file") and "-n" in comando:
        destino = comando.split(" ")[2]  # Obtém o destinatário do arquivo
        filename = comando.split(" ")[3]  # Obtém o nome do arquivo
        part = request["part"]  # Parte do arquivo que está sendo enviada
        data = {
            "data": request["data"],
            "from": nickname,
            "filename": filename,
            "part": part
        }
        if destino in clientes:
            print(
                f"Parte {part} de arquivo \"{filename}\" enviado para {destino}")
            # Envia o arquivo ao destinatário
            server_socket.sendto(
                f"FILE: {str(data)}".encode(), clientes[destino])
        else:
            server_socket.sendto(
                f"Cliente {destino} não encontrado".encode(), client_address)

    # Caso o comando seja inválido
    else:
        server_socket.sendto("Comando inválido".encode(), client_address)


# Função que inicia o servidor UDP
def inicia_servidor(host="localhost", port=40000):
    server_socket = socket(AF_INET, SOCK_DGRAM)  # Cria um socket UDP
    server_socket.bind((host, port))  # Associa o socket a um endereço e porta

    print(f"Servidor está ativo 🚀 em {host}:{port}")

    while True:
        try:
            # Recebe dados do cliente
            request, client_address = server_socket.recvfrom(1024)

            if not request:
                continue

            # Converte a string recebida para um dicionário
            request = ast.literal_eval(request.decode())
            nickname = request["nickname"]
            comando = request["comando"]

            # Processa o comando recebido
            processa_comando(comando, nickname, client_address,
                             server_socket, request)
        except Exception as e:
            print("[ERRO] Exceção ocorrida")
            print(e)
            continue


if __name__ == "__main__":
    inicia_servidor()  # Inicia o servidor
