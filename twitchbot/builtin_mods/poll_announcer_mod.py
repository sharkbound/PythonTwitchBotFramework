from twitchbot import *


class PollAnnouncerMod(Mod):
    name = 'poll_announcer'

    async def on_poll_started(self, channel: Channel, poll: 'PollData'):
        # await channel.send_message(
        #     f'{poll.owner} has started a poll[{poll.id}] => "{poll.title}" that will end in {poll.duration_seconds} seconds - {poll.formatted_choices()} -- '
        #     f'use "{cfg.prefix}vote <choice_id>" to vote'
        # )
        await channel.send_message(
            f'{poll.title} ~ {poll.formatted_choices()} ~ '
            f'{cfg.prefix}vote <choice_id> ~ ends in {poll.seconds_left} seconds ~ poll id: {poll.id}'
        )

    async def on_poll_ended(self, channel: Channel, poll: 'PollData'):
        await channel.send_message(f'{poll.title} ~ {poll.format_poll_results()}')
        # await channel.send_message(f'poll#{poll.id} ended: "{poll.title}", results >> {poll.format_poll_results()}')
