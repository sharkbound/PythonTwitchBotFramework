from socket import socket

HOST = input('enter command server host (leave blank for "localhost"): ').strip() or 'localhost'
PORT = int(input('enter command server port (leave blank for 1337): ').strip() or 1337)

s = socket()
s.connect((HOST, PORT))
SIZE = 300


def read():
    return s.recv(SIZE).decode()


def send(text):
    s.send(f'{text}\n'.encode())


# prints the welcome message
print(read())

# wait for a valid channel to be selected
msg = ''
channel = ''

while True:
    msg = read()
    if 'quit' in msg:
        break

    print(msg)
    channel = input('>>> ')
    send(channel)

# channel was selected, now start the command/message send loop
while True:
    send(input(f'({channel}): '))
