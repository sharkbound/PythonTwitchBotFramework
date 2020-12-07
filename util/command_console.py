from socket import socket
import json


class Connection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket()
        self.socket.connect((host, port))

    def read(self, size=300) -> str:
        return self.socket.recv(size).decode().strip()

    def read_json(self, size=300) -> dict:
        try:
            return json.loads(self.read())
        except (json.JSONDecoder, TypeError):
            return {}

    def send(self, text: str):
        self.socket.send(f'{text}\n'.encode())

    def send_json(self, **kwargs):
        self.send(json.dumps(kwargs))


def run():
    host = input('enter command server host (leave blank for "localhost"): ').strip() or 'localhost'
    port = int(input('enter command server port (leave blank for 1337): ').strip() or 1337)
    connection = Connection(host, port)

    while True:
        data = connection.read_json()
        print(data)
        connection.send(input())


if __name__ == '__main__':
    run()
