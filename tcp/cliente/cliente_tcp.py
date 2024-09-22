from socket import *
import threading

nickname = None

def receive_messages(client_socket):
    global nickname

    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break

            if message.startswith('Este nickname já está em uso'.encode()):
                nickname = None

            print(message.decode('utf-8'))
        except Exception as e:
            print("[ERRO] Conexão perdida.")
            print(e)
            break

def inicia_cliente(host="0.0.0.0", port=40000):
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

        comando = {
            "comando": comando,
            "nickname": nickname
        }

        client.send(str(comando).encode())

if __name__ == "__main__":
    inicia_cliente()