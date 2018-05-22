#! python3.6

from asyncio import get_event_loop
from twitchbot import BaseBot


async def main():
    bot = await BaseBot.create()

    await bot.start()


get_event_loop().run_until_complete(main())
