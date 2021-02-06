import _thread
import json
import os
import socket
import random
import sys
from os import listdir
from os.path import isfile, join

from tqdm import tqdm

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils import constants
from utils.functions import log, convert_size


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


def listen_to_other_clients(server, port):
    log(port)
    log(f'Wait for connections on port {port}')

    # wait for connection from another clients that want to download file
    while True:
        conn, address = server.accept()
        log(f'Accept connection from {address[0]}:{address[1]}')
        data = json.loads(conn.recv(4096).decode())
        path = join(data['folder'], data['filename'])

        # to be sure that file exists
        if os.path.exists(path):
            file = open(path, 'rb')
            conn.send(file.read())
        else:
            conn.send('No such file'.encode())

        conn.close()


def main():

    listening_server, listening_port = init_server_connection()
    listening_server.listen(5)

    _thread.start_new_thread(listen_to_other_clients, (listening_server, listening_port))

    s = socket.socket()

    # Define the port on which you want to connect
    server_host = constants.host
    server_port = constants.port

    # connect to the server on local computer
    s.connect((server_host, server_port))

    # send port on which client will listen other clients
    s.send(str(listening_port).encode())
    s.recv(1024)

    while True:
        # get action from user
        action = input('1) Get list\n2) Share folder\n3) Download file\n4) Exit\n')
        if action.lower() in ['1', 'get']:
            # send action
            s.send(f'GET'.encode())

            # receive list of files
            buffer = ''
            while '\0' not in buffer:
                buffer += s.recv(4096).decode()
            files = json.loads(buffer[0:buffer.index('\0')])['files']

            # display in cli
            print()
            for i, file in enumerate(files):
                log(f'{i + 1}. name: {file[0]}, size: {convert_size(int(file[1]))}')
            print()

        elif action.lower() in ['2', 'share']:
            # make sure path exists
            while True:
                path = input('Please enter absolute path of sharing folder\n')
                if os.path.exists(path):
                    break

            # send command
            s.send(f'SHARE'.encode())
            s.recv(1024).decode()

            # send path to store
            s.send(f'{path}'.encode())
            s.recv(1024).decode()

            # get all files in directory and store in list
            files = []
            for f in listdir(path):
                if isfile(join(path, f)):
                    files.append([f, os.path.getsize(join(path, f))])
            data = {'files': files}

            # send array through socket to server
            s.send(f'{json.dumps(data)}\0'.encode())
            log(s.recv(1024).decode())

        elif action.lower() in ['3', 'download']:
            # get filename
            filename = input('Please enter filename\n')

            # send command
            s.send(f'DOWNLOAD'.encode())
            s.recv(1024)

            # send filename
            s.send(f'{filename}'.encode())

            # get info about client that has given file
            user = json.loads(s.recv(4096).decode())

            # initiate another client socket to download file
            file_socket = socket.socket()
            file_socket.connect((user['host'], int(user['port'])))

            # send to filename to client that has given file
            data = {'filename': filename, 'folder': user['folder']}
            file_socket.send(json.dumps(data).encode())

            # initiate progress bar
            buffer_size = 1024
            progress = tqdm(range(int(user['size'])),
                            f'Receiving {filename}',
                            unit='B',
                            unit_scale=True,
                            unit_divisor=buffer_size
                            )

            # create folder that will store file
            if not os.path.exists('./Downloads'):
                os.mkdir('./Downloads')

            # start download
            with open(f'./Downloads/{filename}', 'wb') as file:
                while True:
                    # read 1024 bytes from the socket (receive)
                    bytes_read = file_socket.recv(buffer_size)
                    if not bytes_read:
                        # nothing is received
                        # file transmitting is done
                        break
                    # write to the file the bytes we just received
                    file.write(bytes_read)

                    # update progress bar
                    progress.update(len(bytes_read))

            # after download, close connection
            file_socket.close()

        elif action.lower() in ['4', 'exit']:
            break
    s.close()


if __name__ == '__main__':
    main()
