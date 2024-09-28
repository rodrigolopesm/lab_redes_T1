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

    # Função que recebe mensagens do servidor
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break

            if message.startswith("Este nickname já está em uso".encode()):
                nickname = None

            elif message.startswith('FILE: '.encode()):
                text_data = message.decode('utf-8').split("FILE: ")[1]
                data = ast.literal_eval(text_data)
                print(
                    f"Arquivo \"{data['filename']}\" recebido de {data['from']}")
                write_file(data["filename"], data["data"], data["from"])
                continue
            print(message.decode('utf-8'))
        except Exception as e:
            print("[ERRO] Conexão perdida.")
            print(e)
            break


def send_file(client_socket, comando):
    filename = comando.split(" ")[3]

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
    # Função que inicia o cliente e se conecta ao servidor
    client = socket(AF_INET, SOCK_STREAM)  # Cria um socket TCP
    client.connect((host, port))

    # Cria uma thread para receber mensagens do servidor
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    print("Você está conectado ao servidor. Digite /reg <nickname> para se registrar\n")
    print("Para enviar mensagens, digite /msg <mensagem> ou /msg -n <destino> <mensagem>")
    print("Para enviar arquivos, digite /file -n <destino> <nome do arquivo>")

    while True:
        comando = input("")

        # Verifica se o comando é para registrar um nickname
        if comando.startswith("/reg"):
            global nickname
            if nickname is not None:
                print("Você já está registrado")
                continue
            nickname = comando.split(" ")[1]
        elif comando.startswith("/file"):
            send_file(client, comando)
            continue

        # Prepara o comando para envio, incluindo o nickname
        comando = {"comando": comando, "nickname": nickname}

        client.send(str(comando).encode())


# Ponto de entrada do script
if __name__ == "__main__":
    inicia_cliente()  # Inicia a função que conecta o cliente ao servidor
