from socket import socket

s = socket()
s.connect(('localhost', 1337))
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
