#! python3.6

from asyncio import get_event_loop

from twitchbot.bots import BaseBot
from twitchbot.command import load_commands_from_folder


async def main():
    bot = await BaseBot.create()

    await bot.start()


get_event_loop().run_until_complete(main())
