import socket
import hmac
import hashlib
import secrets
import time
import keyboard
import sys
import json
import os


NONCES_FILE_PATH = 'nonces.json'
LOGS_FILE_PATH = 'logs.txt'


def close_server(sock):
    '''Cierra el servidor y el programa.'''
    print('Cerrando servidor...')
    sock.close()
    sys.exit(0)


def load_files():
    '''Carga los ficheros de NONCE y logs.'''

    # Crea un fichero para almacenar los NONCE si no existe
    if not os.path.exists(NONCES_FILE_PATH):
        json.dump({'nonces': []}, open(
            NONCES_FILE_PATH, 'w', encoding='utf-8'))

    # Carga los NONCE del fichero
    nonces_json = json.load(open(NONCES_FILE_PATH, 'r', encoding='utf-8'))

    # Crear un fichero para almacenar los logs
    if not os.path.exists(LOGS_FILE_PATH):
        open(LOGS_FILE_PATH, 'w', encoding='utf-8')

    # Cargar el fichero de logs
    logs_txt = open(LOGS_FILE_PATH, 'r+', encoding='utf-8')

    return nonces_json, logs_txt


def create_nonce(nonces_json):
    '''Genera un NONCE aleatorio y lo añade al fichero de NONCE.'''

    # Inicializar NONCE
    nonce = 0

    while nonce == 0 or nonce in nonces_json["nonces"]:
        # Generar NONCE aleatorio
        nonce = str(secrets.randbelow(2**256)).encode()

        # Comprobar que el NONCE no existe
        if nonce not in nonces_json["nonces"]:
            # Añadir NONCE al fichero
            with open('nonces.json', 'r+') as file:
                nonces_json["nonces"].append(nonce.decode())
                file.seek(0)
                json.dump(nonces_json, file)
                file.truncate()

            print('NONCE generado:', nonce.decode())

            return nonce


def check_hmac(nonce, data, hmac_received, logs_txt):
    '''Comprueba el HMAC y procesa la transferencia.'''

    # Calcula el HMAC
    hmac_calculated = hmac.new(
        nonce, data, hashlib.sha256).hexdigest()

    print('HMAC calculado:', hmac_calculated)

    # Comprueba que el HMAC coincide
    if hmac_calculated != hmac_received.decode():
        # Mensaje de error
        message = 'Error: El mensaje ha sido alterado o no se puede verificar la fuente.'
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        logs_txt.write(f"[{current_time}]: {message}\n")
    else:
        # Procesa la transferencia
        transfer = data.decode().split(',')
        account_from = transfer[0]
        account_to = transfer[1]
        amount = transfer[2]
        message = 'Transferencia de {} a {} por un valor de {} realizada.'.format(
            account_from, account_to, amount)

    return message


def main():
    # Carga los ficheros
    nonces_json, logs_txt = load_files()

    # Crea un socket y escucha las conexiones entrantes
    server_address = ('localhost', 3030)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen(1)
    print('Servidor iniciado en {}:{}'.format(*server_address))

    # Configurar el manejo de teclas para cerrar el servidor
    keyboard.add_hotkey('ctrl+c', close_server, args=(sock,))

    while True:
        # Espera una conexión
        connection, client_address = sock.accept()
        print('Conexión desde', client_address)

        try:
            # Recibir petición de NONCE
            nonce_request = connection.recv(1024)

            # Conexión sin petición de NONCE
            if nonce_request.decode() != 'NONCE':
                message = 'Error: La petición no es válida, posible ataque de reply.'
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                logs_txt.write(f"[{current_time}]: {message}\n")
                connection.sendall(bytes(message, 'utf-8'))
                continue

            # Generar NONCE
            nonce = create_nonce(nonces_json)

            # Enviar NONCE al cliente
            connection.sendall(nonce)

            # Esperar 30 segundo a los datos, HMAC y clave pública
            print('Esperando transferencia...')

            # Recibe los datos y el HMAC
            data = connection.recv(1024)
            hmac_received = connection.recv(1024)

            # Mostar por pantalla los datos recibidos
            print('Transferencia recibida:', data.decode())
            print('HMAC recibido:', hmac_received.decode())

            # Comprobar el HMAC
            message = check_hmac(nonce, data, hmac_received, logs_txt)
            connection.sendall(bytes(message, 'utf-8'))

        except Exception as e:
            print(e)

        finally:
            # Cierra la conexión
            connection.close()


if __name__ == '__main__':
    main()
