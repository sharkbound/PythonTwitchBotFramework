import asyncio
from .. import util

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

    async def on_successful_update(self):
        """
        called when the API updates without any errors
        """
        pass

    async def on_failed_update(self):
        """
        called when the API encounters a error trying to update
        """
        pass

    def __eq__(self, other):
        if not isinstance(other, Api):
            return False

        return self.user == other.user
