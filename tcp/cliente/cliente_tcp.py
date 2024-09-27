from socket import *
import threading

nickname = None


def receive_messages(client_socket):
    global nickname

    # Função que recebe mensagens do servidor
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break

            if message.startswith("Este nickname já está em uso".encode()):
                nickname = None

            print(message.decode("utf-8"))
        except Exception as e:
            print("[ERRO] Conexão perdida.")
            print(e)
            break


def inicia_cliente(host="localhost", port=40000):
    # Função que inicia o cliente e se conecta ao servidor
    client = socket(AF_INET, SOCK_STREAM)  # Cria um socket TCP
    client.connect((host, port))

    # Cria uma thread para receber mensagens do servidor
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    print("Você está conectado ao servidor. Digite /reg <nickname> para se registrar\n")
    print(
        "Para enviar mensagens, digite /msg <mensagem> ou /msg -n <destino> <mensagem>"
    )

    while True:
        comando = input("")

        # Verifica se o comando é para registrar um nickname
        if comando.startswith("/reg"):
            global nickname
            if nickname is not None:
                print("Você já está registrado")
                continue
            nickname = comando.split(" ")[1]
        # Prepara o comando para envio, incluindo o nickname
        comando = {"comando": comando, "nickname": nickname}

        # Envia o comando codificado como string para o servidor
        client.send(str(comando).encode())


# Ponto de entrada do script
if __name__ == "__main__":
    inicia_cliente()  # Inicia a função que conecta o cliente ao servidor
