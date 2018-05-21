#! python3.6

from asyncio import get_event_loop

from bots import BaseBot
from command import load_commands_from_folder


async def main():
    bot = await BaseBot.create()

    load_commands_from_folder('commands')

    await bot.start()


get_event_loop().run_until_complete(main())
