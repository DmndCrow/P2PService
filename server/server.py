import socket
import sys
import random
import _thread

from utils import constants
from utils.functions import log
from db import DB
import ThreadConnection


def main():
    # create socket for connection
    try:
        server_socket = socket.socket()
    except socket.error as e:
        log(e)
        sys.exit(-1)

    # assign port that is not in use
    while True:
        port = random.randint(0, 65535)
        try:
            server_socket.bind(('', port))
            break
        except socket.error as e:
            continue

    log(f'Server is running on port {port}')

    # start database
    db = DB(constants.db_name)

    # listen for incoming connections
    server_socket.listen(5)

    while True:
        # accept connection
        conn, address = server_socket.accept()
        # run thread to handle connection
        _thread.start_new_thread(ThreadConnection.client_connection, (db, conn, address[0], address[1]))


if __name__ == '__main__':
    main()
