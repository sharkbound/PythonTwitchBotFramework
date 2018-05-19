import asyncio
import util

from datetime import datetime


class Api:
    def __init__(self, client_id: str, user: str):
        self.user = user
        self.client_id = client_id
        self.headers = {'Client-ID': client_id}

    async def update(self, log=False):
        pass

    async def update_loop(self, delay=60):
        while True:
            await self.update()
            await asyncio.sleep(delay)

    def __eq__(self, other):
        if not isinstance(other, Api):
            return False

        return self.user == other.user
