import time

from twitchbot import Mod, Message, cfg, normalize_string


class ChannelLastPrivmsgTimeUpdaterMod(Mod):
    async def on_privmsg_received(self, msg: Message):
        if normalize_string(cfg.nick) != normalize_string(msg.author):
            msg.channel.last_privmsg_time = time.time()
