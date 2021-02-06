import json
import os
import socket
import random
import sys
from os import listdir
from os.path import isfile, join

from utils import constants
from utils.functions import log


def init_server_connection():
    # create socket for connection
    try:
        server = socket.socket()
    except socket.error as e:
        log(e)
        sys.exit(-1)

    # assign port that is not in use
    while True:
        port = random.randint(0, 65535)
        try:
            server.bind(('', port))
            break
        except socket.error as e:
            continue
    return server, port


def main():

    listening_server, listening_port = init_server_connection()
    listening_server.listen(5)

    s = socket.socket()

    # Define the port on which you want to connect
    server_host = constants.host
    server_port = 57499

    # connect to the server on local computer
    s.connect((server_host, server_port))

    # send port on which client will listen other clients
    s.send(str(listening_port).encode())
    s.recv(1024)

    while True:
        action = input('1) Get list\n2) Share folder\n3) Download file\n4) Exit\n')
        if action.lower() in ['1', 'get']:
            s.send(f'GET'.encode())

            buffer = ''
            while '\0' not in buffer:
                buffer += s.recv(4096).decode()
            files = json.loads(buffer[0:buffer.index('\0')])['files']
            for i, file in enumerate(files):
                print(f'{i + 1}. {file}')

        elif action.lower() in ['2', 'share']:
            # make sure path exists
            while True:
                path = input('Please enter absolute path to sharing folder\n')
                if os.path.exists(path):
                    break

            # send command
            s.send(f'SHARE'.encode())
            s.recv(1024).decode()

            # send path to store
            s.send(f'{path}'.encode())
            s.recv(1024).decode()

            # get all files in directory and store in list
            files = {'files': [f for f in listdir(path) if isfile(join(path, f))]}
            print(files['files'])
            # send array through socket to server
            s.send(f'{json.dumps(files)}\0'.encode())
            print(s.recv(1024).decode())
        elif action.lower() in ['3', 'download']:
            filename = input('Please enter absolute path to sharing folder\n')
            s.send(f'DOWNLOAD'.encode())
            s.recv(1024)
            s.send(f'{filename}'.encode())
            print(s.recv(1024).decode())
        elif action.lower() in ['4', 'exit']:
            break
    s.close()


if __name__ == '__main__':
    main()


# 1) get list
# 2) share location
# 3) download
# 4) exit
