import json

from db import Action
from utils.functions import log


def client_connection(db, conn, host, port, listen_port):
    log(f'Client connected from {host}:{port}')

    # add user to database
    db.AddUser(host, port, listen_port)

    while True:
        # get action from client
        message = conn.recv(1024).decode()

        # if user wants to see files
        if message == Action.get:
            # get all files that dont belong to user
            files = {'files': db.GetFiles(host, port)}
            conn.send(f'{json.dumps(files)}\0'.encode())

        # if user wants to share his files
        if message == Action.share:
            conn.send('ok'.encode())
            # get path that stores files
            path = conn.recv(1024).decode()
            conn.send('Path Saved'.encode())

            # get all files that are not in provided folder
            buffer = ''
            while '\0' not in buffer:
                buffer += conn.recv(4096).decode()

            files = json.loads(buffer[0:buffer.index('\0')])['files']
            conn.send('SAVED'.encode())

            # save path in database
            db.AssignFolderPath(host, port, path, files)

        # if user wants to download file
        if message == Action.download:
            conn.send('ok'.encode())
            # get file name
            file = conn.recv(4096).decode()

            # find user that has this file and return info about it
            data = json.dumps(db.GetFileInfo(host, port, file))
            conn.send(data.encode())

        # if user wants to exit
        if message == Action.exit:
            # remove him from database
            db.DeleteUser(host, port)
            break
    log(f'Connection closed with {host}:{port}')
    conn.close()
