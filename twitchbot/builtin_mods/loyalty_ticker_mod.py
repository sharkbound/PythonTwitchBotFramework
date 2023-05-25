import time
from asyncio import sleep
from typing import Dict

from twitchbot import Mod, add_balance, session, cfg, task_running, add_task, stop_task, Message


class LoyaltyTicketMod(Mod):
    name = "LoyaltyTicketMod"
    LOYALTY_TICKER_TASK_NAME = "LoyaltyTicketModTask"
    REMOVE_FROM_VIEWERS_INACTIVE_SECONDS = 60 * 30  # 30 minutes

    def __init__(self):
        super().__init__()
        self.channel_viewers: Dict[str, Dict[str, float]] = {}

    def viewers_for_channel(self, channel_name: str) -> Dict[str, float]:
        viewers = self.channel_viewers.get(channel_name)
        if viewers is None:
            viewers = {}
            self.channel_viewers[channel_name] = viewers
        return viewers

    async def loaded(self):
        if cfg.loyalty_interval == -1:
            print('loyalty_interval in config is -1, loyalty ticker WILL NOT start')
            return

        if not task_running(self.LOYALTY_TICKER_TASK_NAME):
            add_task(self.LOYALTY_TICKER_TASK_NAME, self._ticker_loop())

        self.channel_viewers.clear()

    async def unloaded(self):
        stop_task(self.LOYALTY_TICKER_TASK_NAME)
        self.channel_viewers.clear()

    async def on_privmsg_received(self, msg: Message):
        self.viewers_for_channel(msg.channel_name)[msg.author] = time.time()

    async def _ticker_loop(self):
        print(f'loyalty ticker started!')
        while True:
            now = time.time()
            for channel_name, viewers in self.channel_viewers.items():
                to_remove = []
                for viewer, last_chat_time in viewers.items():
                    # has the viewer been inactive for too long?
                    if abs(now - last_chat_time) >= self.REMOVE_FROM_VIEWERS_INACTIVE_SECONDS:
                        to_remove.append(viewer)
                        continue
                    # viewer is still active, so give them balance
                    add_balance(channel_name, viewer, cfg.loyalty_amount, commit=False)

                for viewer in to_remove:
                    del viewers[viewer]

                session.commit()
            await sleep(cfg.loyalty_interval)
