from .util import add_task, task_running, stop_task
from asyncio import sleep
from .database import add_balance, session
from .config import cfg
from .channel import channels

LOYALTY_TICKER_TASK_NAME = '_loyalty_ticker'


async def _ticker_loop():
    while True:
        for channel in channels.values():
            for viewer in channel.chatters.all_viewers:
                add_balance(channel.name, viewer, cfg.loyalty_amount, commit=False)
                await sleep(.2)
            session.commit()

        await sleep(cfg.loyalty_interval)


def start_loyalty_ticker():
    if not task_running(LOYALTY_TICKER_TASK_NAME):
        add_task(LOYALTY_TICKER_TASK_NAME, _ticker_loop())


def stop_loyalty_ticker():
    stop_task(LOYALTY_TICKER_TASK_NAME)


start_loyalty_ticker()
