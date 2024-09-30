import os
from socket import *
import threading
import ast
import time

nickname = None  # Variável global para armazenar o nickname do cliente


# Função para escrever partes de arquivo recebidas.
def write_file(filename, data, sender):
    final_filename = f"{sender} - {filename}"  # Adiciona o remetente ao nome do arquivo
    if isinstance(data, bytes):
        data = data.decode('utf-8')  # Decodifica dados binários em string

    lines = data.splitlines()  # Divide o conteúdo em linhas
    normalized_data = '\n'.join(lines)  # Normaliza as quebras de linha

    with open(final_filename, 'a') as f:
        f.write(normalized_data)  # Grava os dados no arquivo


# Função que recebe mensagens do servidor
def receive_messages(client_socket, server_address):
    global nickname

    while True:
        try:
            # Recebe mensagens do servidor
            message, _ = client_socket.recvfrom(1024)
            if not message:
                break

            # Verifica se o nickname já está em uso
            if message.startswith('Este nickname já está em uso'.encode()):
                nickname = None
            # Verifica se é um arquivo sendo recebido
            elif message.startswith('FILE: '.encode()):
                text_data = message.decode('utf-8').split("FILE: ")[1]
                data = ast.literal_eval(text_data)
                part = data["part"]
                print(f"Parte {part} de arquivo \"{data['filename']}\" recebido de {data['from']}")
                write_file(data["filename"], data["data"], data["from"])  # Grava a parte recebida
                continue

            print(message.decode('utf-8'))  # Exibe mensagens de texto recebidas
        except Exception as e:
            print(e)
            break


# Função para enviar arquivos ao servidor
def send_file(client_socket, server_address, comando):
    filename = comando.split(" ")[3]  # Extrai o nome do arquivo do comando

    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")  # Verifica se o arquivo existe
        return

    with open(filename, 'rb') as f:
        part = 0
        while True:
            file_data = f.read(512)  # Lê o arquivo em blocos de 512 bytes
            if not file_data:
                break

            # Monta o dicionário de dados do arquivo
            data = {
                "comando": comando,
                "data": file_data,
                "nickname": nickname,
                "part": part
            }
            part += 1
            # Envia cada parte do arquivo
            client_socket.sendto(str(data).encode(), server_address)
            time.sleep(0.05)

    print(f"File {filename} sent successfully.")  # Confirmação de envio


# Função que inicia o cliente UDP
def inicia_cliente(host="localhost", port=40000):
    client = socket(AF_INET, SOCK_DGRAM)  # Cria um socket UDP
    server_address = (host, port)
    startedListener = False  # Controle para iniciar a thread de recebimento

    print("Você está conectado ao servidor. Digite /reg <nickname> para se registrar\n")
    print("Para enviar mensagens, digite /msg <mensagem> ou /msg -n <destino> <mensagem>")
    print("Para enviar arquivos, digite /file -n <destino> <nome do arquivo>")

    while True:
        comando = input("")  # Recebe comando do usuário

        if comando.startswith("/reg"):
            global nickname
            if nickname is not None:
                print("Você já está registrado")
                continue
            nickname = comando.split(" ")[1]  # Define o nickname

        elif comando.startswith("/file"):
            send_file(client, server_address, comando)  # Envia arquivo
            continue

        # Monta o dicionário com o comando e nickname
        comando_data = {
            "comando": comando,
            "nickname": nickname
        }

        client.sendto(str(comando_data).encode(), server_address)  # Envia comando ao servidor

        if not startedListener:
            # Inicia thread para receber mensagens do servidor
            receive_thread = threading.Thread(target=receive_messages, args=(client, server_address))
            receive_thread.start()
            startedListener = True  # Marca que a thread de recebimento foi iniciada


if __name__ == "__main__":
    inicia_cliente()  # Inicia o cliente
