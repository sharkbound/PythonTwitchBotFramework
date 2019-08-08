import asyncio
import ssl

from ..config import get_nick, get_oauth
from ..irc import Irc

__all__ = ('SSL_PORT', 'HTTP_PORT', 'create_connection', 'send_auth', 'create_irc')

SSL_PORT = 443
HTTP_PORT = 6667


async def create_connection():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ssl_context.get_ciphers()
    return await asyncio.open_connection('irc.chat.twitch.tv', SSL_PORT, ssl=ssl_context)


def send_auth(irc: Irc):
    irc.send_all(
        f'PASS {get_oauth()}',
        f'NICK {get_nick()}')


async def create_irc() -> Irc:
    reader, writer = await create_connection()
    return Irc(reader=reader, writer=writer)
