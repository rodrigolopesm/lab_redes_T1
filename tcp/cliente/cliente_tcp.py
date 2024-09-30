from socket import *
import threading
import os
import ast
import time

nickname = None  # Variável global para armazenar o nickname do cliente


def write_file(filename, data, sender):
    # Função para gravar partes de arquivo recebidas
    # Adiciona o remetente ao nome do arquivo
    final_filename = f"{sender} - {filename}"
    if isinstance(data, bytes):
        data = data.decode('utf-8')

    lines = data.splitlines()  # Normaliza as quebras de linha
    normalized_data = '\n'.join(lines)

    with open(final_filename, 'a') as f:
        f.write(normalized_data)  # Grava os dados recebidos no arquivo


def receive_messages(client_socket):
    global nickname

    # Função que recebe mensagens do servidor
    while True:
        try:
            message = client_socket.recv(1024)  # Recebe mensagens do servidor
            if not message:
                break

            if message.startswith("Este nickname já está em uso".encode()):
                nickname = None  # Reseta o nickname se já estiver em uso

            elif message.startswith('FILE: '.encode()):
                # Tratamento de arquivos recebidos
                text_data = message.decode('utf-8').split("FILE: ")[1]
                data = ast.literal_eval(text_data)
                part = data["part"]
                print(
                    f"Parte {part} de arquivo \"{data['filename']}\" recebido de {data['from']}")
                write_file(data["filename"], data["data"],
                           data["from"])  # Grava a parte recebida
                continue

            # Exibe mensagens de texto no console
            print(message.decode('utf-8'))
        except Exception as e:
            print("[ERRO] Conexão perdida.")
            print(e)
            break


def send_file(client_socket, comando):
    # Função para enviar arquivos ao servidor
    filename = comando.split(" ")[3]

    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")
        return

    with open(filename, 'rb') as f:
        part = 0
        while True:
            file_data = f.read(512)  # Lê o arquivo em partes
            if not file_data:
                break

            data = {
                "comando": comando,
                "data": file_data,
                "nickname": nickname,
                "part": part
            }
            part += 1
            client_socket.send(str(data).encode())  # Envia parte do arquivo
            time.sleep(0.05)

    print(f"File {filename} sent successfully.")  # Confirmação de envio


def inicia_cliente(host="localhost", port=40000):
    # Função que inicia o cliente e conecta ao servidor
    client = socket(AF_INET, SOCK_STREAM)  # Cria socket TCP
    client.connect((host, port))  # Conecta ao servidor

    # Thread para receber mensagens
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    print("Você está conectado ao servidor. Digite /reg <nickname> para se registrar\n")
    print("Para enviar mensagens, digite /msg <mensagem> ou /msg -n <destino> <mensagem>")
    print("Para enviar arquivos, digite /file -n <destino> <nome do arquivo>")

    while True:
        comando = input("")  # Aguarda input do usuário

        if comando.startswith("/reg"):
            # Comando para registro do nickname
            global nickname
            if nickname is not None:
                print("Você já está registrado")
                continue
            nickname = comando.split(" ")[1]  # Define o nickname
        elif comando.startswith("/file"):
            send_file(client, comando)  # Envia arquivo se o comando for /file
            continue

        comando = {"comando": comando, "nickname": nickname}

        client.send(str(comando).encode())  # Envia comando ao servidor


if __name__ == "__main__":
    inicia_cliente()  # Inicia o cliente
