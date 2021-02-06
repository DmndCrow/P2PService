import socket
import sys
import _thread
import os

# To make sure that we can see functions from utils folder
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils import constants
from utils.functions import log
from db import DB
import ThreadConnection


def init_server_connection():
    # create socket for connection
    try:
        server = socket.socket()
    except socket.error as e:
        log(e)
        sys.exit(-1)

    # assign port that is not in use
    port = constants.port
    server.bind(('', port))

    return server, port


def main():
    # create socket for connection
    server, port = init_server_connection()
    log(f'Server is running on port {port}')

    # listen for incoming connections
    server.listen(50)  # Accepts up to 50 connections.

    # start database
    db = DB(constants.db_name)

    while True:
        # accept connection
        conn, address = server.accept()

        # get client listening port
        port = conn.recv(1024).decode()
        conn.send('LISTEN PORT received'.encode())

        # run thread to handle connection
        _thread.start_new_thread(ThreadConnection.client_connection, (db, conn, address[0], address[1], port))


if __name__ == '__main__':
    main()
