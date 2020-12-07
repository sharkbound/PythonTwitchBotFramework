from socket import socket


class Socket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket()
        self.socket.connect((host, port))

    def read(self, size=300) -> str:
        return self.socket.recv(size).decode().strip()

    def write(self, text: str):
        self.socket.send(f'{text}\n'.encode())


def run():
    host = input('enter command server host (leave blank for "localhost"): ').strip() or 'localhost'
    port = int(input('enter command server port (leave blank for 1337): ').strip() or 1337)
    socket = Socket(host, port)
