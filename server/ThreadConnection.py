import json

from db import Action
from utils.functions import log


def client_connection(db, conn, host, port):
    log(f'Client connected from {host}:{port}')

    db.AddUser(host, port)
    while True:
        message = conn.recv(1024).decode()

        if message == Action.get:
            data = db.GetData()
            conn.send(json.dumps(data).encode())
        if message == Action.share:
            conn.send('ok'.encode())
            path = conn.recv(1024).decode()
            db.AssignFolderPath(host, port, path)
            conn.send('Path Saved'.encode())
        if message == Action.download:
            conn.send('ok'.encode())
            file = conn.recv(1024).decode()
            conn.send(file.encode())
        if message == Action.exit:
            db.DeleteUser(host, port)
            break
    log(f'Connection closed with {host}:{port}')
    conn.close()
