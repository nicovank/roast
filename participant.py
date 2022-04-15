from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

import sys

from roast import SessionContext, pre_round, sign_round
from transport import send_obj, recv_obj

class Participant:
    def __init__(self, i, sk_i):
        self.i = i
        self.sk_i = sk_i
        self.spre_i, self.pre_i = pre_round()

    def sign_round(self, ctx, T):
        s_i = sign_round(ctx, T, self.i, self.sk_i, self.spre_i)
        self.spre_i, self.pre_i = pre_round()
        return s_i, self.pre_i

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'usage: {sys.argv[0]} <port>')
        sys.exit(1)

    port = int(sys.argv[1])
    addr = ('localhost', port)

    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
    sock.bind(addr)
    sock.listen()

    while True:
        print('Listening for incoming connections on', addr)

        connection, src = sock.accept()
        print('Accepted connection from', src)

        i, sk_i = recv_obj(connection)
        print(f'Received initialization data as participant {i}')

        participant = Participant(i, sk_i)
        send_obj(connection, (i, None, participant.pre_i))
        print(f'Sent initial pre_i value')

        while True:
            obj = recv_obj(connection)
            if obj is None:
                print('Connection closed')
                break

            ctx, T = obj
            print(f'Received sign_round request')
            s_i, pre_i = participant.sign_round(ctx, T)
            send_obj(connection, (i, s_i, pre_i))
            print(f'Sent sign_round response and next pre_i value')
