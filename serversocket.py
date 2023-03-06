# serversocket.py

import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 3030  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024, socket.MSG_PEEK)
            if len(data)>1024:
                conn.sendall(b"Message too long")
            if not data:
                break
            if len(data)<=1024:
                conn.sendall(data)