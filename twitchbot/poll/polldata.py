__all__ = [
    'PollData',
    'get_channel_poll_by_id',
    'get_active_channel_polls',
    'active_polls',
    'get_active_channel_poll_count',
    'PollVote',
    'poll_event_processor_loop',
    'POLL_CHECK_INTERVAL_SECONDS'
]

from asyncio import sleep
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import List, DefaultDict, Optional, Tuple

from ..channel import Channel
from ..event_util import forward_event

# from ..events import trigger_event
# from ..modloader import trigger_mod_event

POLL_CHECK_INTERVAL_SECONDS = 2

active_polls: DefaultDict[str, List['PollData']] = defaultdict(list)


@dataclass(frozen=True)
class PollVote:
    voter: str
    choice: int


class PollData:
    _last_id = 0

    def __init__(self, channel: Channel, owner: str, title: str, duration_seconds: float, *choices: str):
        self.duration_seconds: float = duration_seconds
        self.choices: List[str] = list(choices)
        self.choices_normalized: List[str] = list(map(self._format, choices))
        self.channel: Channel = channel
        self.votes: List[PollVote] = []
        self.owner = owner
        self.title = title
        self.start_time = datetime.now()

        PollData._last_id += 1
        self.id = PollData._last_id

    @property
    def all_choice_ids(self):
        return {i + 1 for i, _ in enumerate(self.choices)}

    @property
    def done(self):
        return (datetime.now() - self.start_time).total_seconds() > self.duration_seconds

    @property
    def seconds_left(self):
        return max(0, round(self.duration_seconds - (datetime.now() - self.start_time).total_seconds(), 1))

    def _format(self, value: str) -> str:
        return value.lower().strip()

    def is_valid_vote(self, choice_id: int) -> bool:
        return choice_id in self.all_choice_ids

    def add_choice(self, choice: str):
        normalized = self._format(choice)
        if normalized not in self.choices_normalized:
            self.choices.append(choice)
            self.choices_normalized.append(normalized)

    def remove_choice(self, choice: str):
        normalized = self._format(choice)
        if normalized in self.choices_normalized:
            self.choices.remove(choice)
            self.choices_normalized.remove(normalized)

    def has_already_voted(self, username: str):
        return any(v.voter == username for v in self.votes)

    def add_vote(self, voter: str, choice_id: int) -> bool:
        if not self.is_valid_vote(choice_id):
            return False

        self.votes.append(PollVote(voter, choice_id - 1))
        return True

    def format_choices(self):
        return ' '.join(f'{i}) {v}' for i, v in enumerate(self.choices, start=1))

    async def end(self):
        pass

    async def start(self, trigger_event: bool = True):
        await self.channel.send_message(
            f'{self.owner} has started poll "{self.title}" ID({self.id}) that will end in {self.duration_seconds} seconds - {self.format_choices()}'
        )

        self._trigger_start_event(trigger_event)
        active_polls[self.channel_name].append(self)

    def _trigger_start_event(self, trigger_event):
        from ..event_util import forward_event, Event
        if trigger_event:
            forward_event(Event.on_poll_started, self.channel, self)

    @property
    def channel_name(self):
        return self.channel.name.lower().strip()

    def __eq__(self, other):
        return isinstance(other, PollData) and other.id == self.id

    def __repr__(self):
        return f'<{self.__class__.__name__} id={self.id}>'

    def __str__(self):
        return f'<{self.__class__.__name__} title={self.title!r} id={self.id}>'


def get_channel_poll_by_id(channel: str, id: int) -> Optional[PollData]:
    return next(filter(lambda x: x.id == id, active_polls[channel]), None)


def get_active_channel_polls(channel: str) -> Tuple[PollData]:
    return tuple(poll for poll in active_polls[channel] if not poll.done)


def get_active_channel_poll_count(channel: str) -> int:
    return sum(1 for poll in active_polls[channel] if not poll.done)


async def poll_event_processor_loop():
    to_remove = []
    while True:
        for channel_name, polls in active_polls.items():
            for poll in polls:
                if poll.done:
                    to_remove.append((channel_name, poll))

        for channel_name, poll in to_remove:
            from twitchbot import Event

            forward_event(Event.on_poll_ended, poll.channel, poll, channel=poll.channel.name)
            active_polls[channel_name].remove(poll)

        to_remove.clear()
        await sleep(POLL_CHECK_INTERVAL_SECONDS)
