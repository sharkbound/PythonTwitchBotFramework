import asyncio
from ..config import cfg
import ssl

from ..irc import Irc

SSL_PORT = 443
HTTP_PORT = 6667


async def create_connection():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ssl_context.get_ciphers()
    return await asyncio.open_connection('irc.chat.twitch.tv', SSL_PORT, ssl=ssl_context)


def connect(irc: Irc):
    irc.send_all(
        f'PASS {cfg.oauth}',
        f'NICK {cfg.nick}')


async def create_irc() -> Irc:
    reader, writer = await create_connection()
    return Irc(reader=reader, writer=writer)
