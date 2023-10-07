import asyncio

from twitchbot import Mod, channels, get_nick, add_task, stop_task, Message


class ChannelStatUpdaterMod(Mod):
    name = 'channelviewerupdater'
    TASK_NAME = 'channelviewerupdateloop'

    async def channel_update_loop(self):
        while True:
            while not channels:
                await asyncio.sleep(3)

            # convert channels.values() to a tuple to be sure it will not resize while iterating over it
            for channel in tuple(channels.values()):
                # await channel.chatters.update()
                await channel.stats.update() # todo: check this uses queued api requests
                await asyncio.sleep(3)  # delay each updates between channels to avoid sending too many requests too quick
            await asyncio.sleep(120)  # only update channels every 2 minutes

    async def loaded(self):
        add_task(self.TASK_NAME, self.channel_update_loop())

    async def unloaded(self):
        stop_task(self.TASK_NAME)

    async def on_user_state(self, msg: 'Message'):
        msg.channel.is_mod = msg.tags.moderator == 1
        msg.channel.is_vip = msg.tags.vip == 1
        msg.channel.is_broadcaster = msg.tags.broadcaster == 1
        
    
