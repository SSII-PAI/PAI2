import socket
import hashlib
import hmac

'''Prueba 1: Ataque de reply'''


def main():
    # Crea un socket TCP/IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Asigna una dirección y un puerto al socket
    server_address = ('localhost', 3030)
    print('Conectando a {} puerto {}'.format(*server_address))
    sock.connect(server_address)

    try:

        # Envía los datos, HMAC y clave privada
        account_from = input('Cuenta origen: ')
        account_to = input('Cuenta destino: ')
        amount = input('Cantidad: ')
        nonce = input('NONCE: ').encode()
        message = account_from + ',' + account_to + ',' + amount
        hmac_sent = hmac.new(nonce, message.encode(),
                             hashlib.sha256).hexdigest()
        data = message.encode()

        # Envía los datos
        print('Enviando mensaje:', data.decode())
        sock.sendall(data)

        # Envía el HMAC
        print('Enviando HMAC:', hmac_sent)
        sock.sendall(hmac_sent.encode())

        # Espera la respuesta con HMAC
        response = sock.recv(1024)
        print('Respuesta recibida:', response.decode())

    except Exception as e:
        print(e)

    finally:
        # Cierra la conexión
        print('Cerrando conexión')
        sock.close()


if __name__ == '__main__':
    main()
