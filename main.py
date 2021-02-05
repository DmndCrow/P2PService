import socket
from utils import constants


if __name__ == '__main__':
    s = socket.socket()

    s.bind(('', constants.port))

    # put the socket into listening mode
    s.listen(2)
    print("socket is listening")

    while True:
        c, addr = s.accept()
        print('Got connection from', addr)

        # send a thank you message to the client.
        c.send(b'Thank you for connecting')
        c.close()
