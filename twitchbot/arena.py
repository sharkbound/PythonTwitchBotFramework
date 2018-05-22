import asyncio
from asyncio import Future, ensure_future
from twitchbot.channel import Channel
from random import choice
from twitchbot.database import add_balance, get_currency_name
from .config import cfg

ARENA_WAIT_TIME = 30
ARENA_DEFAULT_ENTRY_FEE = 30


class Arena:
    def __init__(self, channel, entry_fee=ARENA_DEFAULT_ENTRY_FEE, min_users=2, on_arena_ended_func=None):
        self.on_arena_ended_func = on_arena_ended_func
        self.future: Future = None
        self.channel: Channel = channel

        self.entry_fee = entry_fee
        self.min_users = min_users
        self.users = set()
        self.running = False

    async def _start_countdown(self, delay):
        curname = get_currency_name(self.channel.name).name

        await self.channel.send_message(
            f'FFA arena has been opened and will start in {delay} seconds! Entry fee is {self.entry_fee} {curname}. '
            f'Type {cfg.prefix}arena to join')

        await asyncio.sleep(delay)
        await self._start_arena()

    async def _start_arena(self):
        if len(self.users) < self.min_users:
            await self.channel.send_message(
                f'not enough users joined the arena to start, everyone that entered was issued a refund')

            for user in self.users:
                add_balance(self.channel.name, user, self.entry_fee)


        else:
            curname = get_currency_name(self.channel.name).name
            winner = choice(tuple(self.users))
            winnings = self.entry_fee * len(self.users)

            add_balance(self.channel.name, winner, winnings)

            print('sne')
            await self.channel.send_message(f'{winner} has won the FFA, and walked away with {winnings} {curname}!')

            self.users.clear()

        if self.on_arena_ended_func:
            self.on_arena_ended_func(self)

        self.running = False

    def add_user(self, user: str):
        if not self.running:
            return False

        self.users.add(user)
        return True

    def start(self):
        self.running = True
        self.future = ensure_future(self._start_countdown(ARENA_WAIT_TIME))
