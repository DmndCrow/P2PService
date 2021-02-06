import json

from db import Action
from utils.functions import log


def client_connection(db, conn, host, port, listen_port):
    log(f'Client connected from {host}:{port}')

    db.AddUser(host, port, listen_port)

    while True:
        message = conn.recv(1024).decode()

        if message == Action.get:
            files = {'files': db.GetFiles(host, port)}
            conn.send(f'{json.dumps(files)}\0'.encode())
        if message == Action.share:
            conn.send('ok'.encode())
            # get path that stores files
            path = conn.recv(1024).decode()
            conn.send('Path Saved'.encode())

            buffer = ''
            while '\0' not in buffer:
                buffer += conn.recv(4096).decode()

            files = json.loads(buffer[0:buffer.index('\0')])['files']
            conn.send('SAVED'.encode())

            # save path in database
            db.AssignFolderPath(host, port, path, files)

        if message == Action.download:
            conn.send('ok'.encode())
            file = conn.recv(1024).decode()
            conn.send(file.encode())
        if message == Action.exit:
            db.DeleteUser(host, port)
            break
    log(f'Connection closed with {host}:{port}')
    conn.close()
