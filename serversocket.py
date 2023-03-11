import socket
import hmac
import hashlib
import random
import time
import keyboard
import sys
import json
import os

def close_server(sock):
    print('Cerrando servidor...')
    sock.close()
    sys.exit(0)

def main():
    # Crea un fichero para almacenar los NONCE si no existe
    nonces_file = 'nonces.json'
    if not os.path.exists(nonces_file):
        json.dump({'nonces': []}, open(nonces_file, 'w'))
    
    # Carga los NONCE del fichero
    nonces_json = json.load(open(nonces_file, 'r'))
    
    # Crea un socket y escucha las conexiones entrantes
    server_address = ('localhost', 3030)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen(1)
    print('Servidor iniciado en {}:{}'.format(*server_address))
    
    # Configurar el manejo de teclas
    keyboard.add_hotkey('ctrl+c', close_server, args=(sock,))

    while True:
        # Espera una conexión
        connection, client_address = sock.accept()
        print('Conexión desde', client_address)

        try:
            # Recibir petición de NONCE
            nonce_request = connection.recv(1024)

            if nonce_request.decode() == 'NONCE':
                # Inicializar NONCE
                nonce = 0

                while nonce == 0 or nonce in nonces_json["nonces"]:
                    # Generar NONCE aleatorio
                    nonce = str(random.randint(0, 2^256)).encode()

                    # Comprobar que el NONCE no existe
                    if nonce not in nonces_json["nonces"]:
                        # Añadir NONCE al fichero
                        with open(nonces_file, 'r+') as file:
                            nonces_json["nonces"].append(nonce.decode())
                            file.seek(0)
                            json.dump(nonces_json, file)
                            file.truncate()
                        
                        print('NONCE generado:', nonce.decode())

                        # Enviar NONCE al cliente
                        connection.sendall(nonce)
                        break

            # Esperar 30 segundo a los datos, HMAC y clave pública
            print('Esperando transferencia...')

            # Recibe los datos y el HMAC
            data = connection.recv(1024)
            hmac_received = connection.recv(1024)

            # Mostar por pantalla los datos recibidos
            print('Transferencia recibida:', data.decode())
            print('HMAC recibido:', hmac_received.decode())

            # Verifica el HMAC
            hmac_calculated = hmac.new(
                nonce, data, hashlib.sha256).hexdigest()

            print('HMAC calculado:', hmac_calculated)

            if hmac_calculated != hmac_received.decode():
                message = 'Error: El mensaje ha sido alterado o no se puede verificar la fuente.'
            else:
                # Procesa la transferencia
                transfer = data.decode().split(',')
                account_from = transfer[0]
                account_to = transfer[1]
                amount = transfer[2]
                message = 'Transferencia de {} a {} por un valor de {} realizada.'.format(
                    account_from, account_to, amount)

            connection.sendall(bytes(message, 'utf-8'))
            
        except Exception as e:
            print(e)

        finally:
            # Cierra la conexión
            connection.close()


if __name__ == '__main__':
    main()
