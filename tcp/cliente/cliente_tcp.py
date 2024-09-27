from socket import *
import threading
import os
import ast

nickname = None


def write_file(filename, data, sender):
    final_filename = f"{sender} - {filename}"
    if not os.path.exists(final_filename):
        with open(final_filename, 'w') as f:
            f.write('')
    with open(final_filename, 'wb') as f:
        f.write(data)


def receive_messages(client_socket):
    global nickname

    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break

            if message.startswith('Este nickname já está em uso'.encode()):
                nickname = None

            elif message.startswith('FILE: '.encode()):
                text_data = message.decode('utf-8').split("FILE: ")[1]
                data = ast.literal_eval(text_data)
                write_file(data["filename"], data["data"], data["from"])
                continue
            print(message.decode('utf-8'))
        except Exception as e:
            print("[ERRO] Conexão perdida.")
            print(e)
            break


def send_file(client_socket, comando):
    filename = comando.split(" ")[1]

    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")
        return

    with open(filename, 'rb') as f:
        while True:
            file_data = f.read(512)
            if not file_data:
                break

            data = {
                "comando": comando,
                "data": file_data,
                "nickname": nickname,
            }
            client_socket.send(str(data).encode())

    print(f"File {filename} sent successfully.")


def inicia_cliente(host="localhost", port=40000):
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((host, port))

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

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

        elif comando.startswith("/file"):
            send_file(client, comando)
            continue

        comando = {
            "comando": comando,
            "nickname": nickname
        }

        client.send(str(comando).encode())


if __name__ == "__main__":
    inicia_cliente()
