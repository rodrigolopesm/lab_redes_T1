from socket import *
import threading
import ast

# Dicionário que armazenará os clientes conectados, onde a chave é o nickname e o valor é o socket.
clientes = {}


def processa_cliente(client_socket):
    def broadcast(msg, sender):
        for client in clientes:
            if (
                client != sender
            ):  # Garante que o remetente não receba a própria mensagem.
                client_socket = clientes[client]
                client_socket.send(
                    msg.encode()
                )  # Envia a mensagem para cada cliente conectado.

    def armazena_cliente(nickname, socket):
        if nickname is not None and nickname not in clientes:
            clientes[nickname] = socket
            return True
        return False

    def processa_comando(comando, nickname, request):
        if nickname is None:
            client_socket.send(
                "Para enviar mensagens, você precisa se registrar".encode()
            )
            return

        # Comando para registrar o cliente.
        if comando.startswith("/reg"):
            if armazena_cliente(nickname, client_socket) is True:
                client_socket.send("Você foi registrado com sucesso!".encode())
                print(f"Cliente {nickname} registrado!")
            else:
                client_socket.send("Este nickname já está em uso".encode())

        # Envio de mensagem pública para todos os clientes.
        elif comando.startswith("/msg") and not "-n" in comando:
            msg = comando.split("/msg ")[1]
            msg = f"{nickname}: {msg}"

            # Envia a mensagem para todos os clientes.
            broadcast(msg, nickname)
            print(f'Mensagem: "{msg}"')

        # Envio de mensagem privada para um cliente específico. /msg -n <destino> <mensagem>
        elif comando.startswith("/msg") and "-n" in comando:
            msg = comando.split("/msg -n ")[1]
            destino = msg.split(" ")[0]
            msg_text = comando.split(f"/msg -n {destino} ")[1]
            msg = f"{nickname}: {msg_text}"

            if destino in clientes:
                print(f'Mensagem para {destino}: "{msg}"')
                clientes[destino].send(msg.encode())
            else:
                client_socket.send(
                    f"Cliente {destino} não encontrado".encode())
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
                clientes[destino].send(f"FILE: {str(data)}".encode())
            else:
                clientes[destino].sendto(
                    f"Cliente {destino} não encontrado".encode())
        else:
            client_socket.send("Comando inválido".encode())

    # Loop principal
    while True:
        try:
            # Recebe dados do cliente
            request = client_socket.recv(1024).decode()

            if not request:
                break

            # Converte a string recebida para um dicionário usando ast.literal_eval.
            request = ast.literal_eval(request)

            nickname = request["nickname"]
            comando = request["comando"]

            processa_comando(comando, nickname, request)
        except Exception as e:
            print("[ERRO] Exceção ocorrida")
            print(e)
            continue


# Função para iniciar o servidor e aceitar conexões dos clientes.
def inicia_servidor(host="localhost", port=40000):
    server = socket(AF_INET, SOCK_STREAM)  # Cria um socket TCP/IP.
    # Associa o socket a um endereço e porta especificados.
    server.bind((host, port))
    server.listen()
    print(f"Servidor está ativo 🚀 em {host}:{port}")

    while True:
        client_socket, addr = server.accept()

        # Inicia uma nova thread para lidar com o cliente conectado, sem bloquear o servidor.
        thread = threading.Thread(
            target=processa_cliente, args=(client_socket,))
        thread.start()


if __name__ == "__main__":
    inicia_servidor()
