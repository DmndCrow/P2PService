import json
import os
import socket

from utils import constants


def main():
    s = socket.socket()

    # Define the port on which you want to connect
    host = constants.host
    port = 6193

    # connect to the server on local computer
    s.connect((host, port))

    while True:
        action = input('1) Get list\n2) Share folder\n3) Download file\n4) Exit\n')
        if action.lower() in ['1', 'get']:
            s.send(f'GET'.encode())
            print(json.loads(s.recv(1024).decode()))
        elif action.lower() in ['2', 'share']:
            while True:
                path = input('Please enter absolute path to sharing folder\n')
                if os.path.exists(path):
                    break
            s.send(f'SHARE'.encode())
            s.recv(1024)
            s.send(f'{path}'.encode())
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
