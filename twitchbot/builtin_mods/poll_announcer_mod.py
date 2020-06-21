from twitchbot import *


class PollAnnouncerMod(Mod):
    name = 'poll_announcer'

    async def on_poll_started(self, channel: Channel, poll: 'PollData'):
        await channel.send_message(
            f'{poll.owner} has started poll "{poll.title}" ID({poll.id}) that will end in {poll.duration_seconds} seconds - {poll.format_choices()}'
        )

    async def on_poll_ended(self, channel: Channel, poll: 'PollData'):
        await channel.send_message(f'poll ended: {poll}')
