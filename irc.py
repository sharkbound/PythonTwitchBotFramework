from asyncio import StreamWriter, StreamReader


class Irc:
    def __init__(self, reader, writer):
        self.reader: StreamReader = reader
        self.writer: StreamWriter = writer

    def send(self, msg):
        self.writer.write(f'{msg}\r\n'.encode())

    def send_all(self, *msgs):
        for msg in msgs:
            self.send(msg)

    async def get_next_message(self):
        return (await self.reader.readline()).decode().strip()

    def send_pong(self):
        self.send('PONG :tmi.twitch.tv')
