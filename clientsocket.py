# clientsocket.py

import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 3030  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    message = b"Hello, world"
    buffer = 1024
    #Split the message in chunks of 1024 bytes
    if len(message)>buffer:
        splitted_message=[message[i:i+buffer] for i in range(0, len(message), buffer)]
        data = b""
        for chunk in splitted_message:
            s.sendall(chunk)
            data += s.recv(buffer)
    else:
        s.sendall(b"Hello, world")
        data = s.recv(buffer)

print(f"Received {data!r}")