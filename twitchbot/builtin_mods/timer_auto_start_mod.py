from twitchbot import Mod, get_all_message_timers, Channel, set_message_timer_active


class TimerAutoStartMod(Mod):
    name = 'timerautostartmod'

    async def on_channel_joined(self, channel: Channel):
        timers = get_all_message_timers(channel.name)
        for timer in timers:
            set_message_timer_active(channel.name, timer.name, True)

        print(f'started the following timers for channel "{channel.name}": {", ".join(timer.name for timer in timers)}')
