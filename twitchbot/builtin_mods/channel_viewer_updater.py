import asyncio

from twitchbot import Mod, channels, get_nick, add_task, stop_task


class ChannelViewUpdaterMod(Mod):
    name = 'channelviewerupdater'
    TASK_NAME = 'channelviewerupdateloop'

    async def channel_update_loop(self):
        while True:
            while not channels:
                await asyncio.sleep(3)

            # convert channels.values() to a tuple to be sure it will not resize while iterating over it
            for channel in tuple(channels.values()):
                await channel.chatters.update()
                await channel.stats.update()
                channel.is_mod = get_nick().lower() in channel.chatters.mods
                channel.is_vip = get_nick().lower() in channel.chatters.vips
                await asyncio.sleep(5)  # delay each updates between channels to avoid sending too many requests too quick
            await asyncio.sleep(120)  # only update channels every 2 minutes

    async def loaded(self):
        add_task(self.TASK_NAME, self.channel_update_loop())

    async def unloaded(self):
        stop_task(self.TASK_NAME)
