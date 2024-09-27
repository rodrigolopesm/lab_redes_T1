from socket import *
import threading

nickname = None


def receive_messages(client_socket, server_address):
    global nickname

    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            if not message:
                break

            if message.startswith('Este nickname já está em uso'.encode()):
                nickname = None

            print(message.decode('utf-8'))
        except Exception as e:
            print(e)
            break


def inicia_cliente(host="localhost", port=40000):
    client = socket(AF_INET, SOCK_DGRAM)
    server_address = (host, port)
    startedListener = False

    print("Você está conectado ao servidor. Digite /reg <nickname> para se registrar\n")
    print("Para enviar mensagens, digite /msg <mensagem> ou /msg -n <destino> <mensagem>")

    while True:
        comando = input("")

        if comando.startswith("/reg"):
            global nickname
            if nickname is not None:
                print("Você já está registrado")
                continue
            nickname = comando.split(" ")[1]

        comando_data = {
            "comando": comando,
            "nickname": nickname
        }

        client.sendto(str(comando_data).encode(), server_address)
        if (not startedListener):
            receive_thread = threading.Thread(
                target=receive_messages, args=(client, server_address))
            receive_thread.start()
            startedListener = True


if __name__ == "__main__":
    inicia_cliente()
