from typing import Tuple, Union, List

from .models import PubSubData
from .. import cached_property
from .twitch_poll_vote_choice import TwitchPollVoteChoice

__all__ = [
    'PubSubPollData'
]


class PubSubPollData:
    def __init__(self, data: PubSubData):
        self.data = data

    @cached_property
    def poll_data_dict(self):
        return self.data.message_data.get('poll', {})

    @property
    def poll_id(self):
        return self.poll_data_dict.get('poll_id', '')

    @property
    def poll_owner_id(self):
        return self.poll_data_dict.get('owned_by', '')

    @property
    def poll_creator_id(self):
        return self.poll_data_dict.get('created_by', '')

    @property
    def poll_title(self):
        return self.poll_data_dict.get('title', '')

    @property
    def poll_duration_seconds(self):
        return self.poll_data_dict.get('duration_seconds', -1)

    @property
    def poll_status(self):
        return self.poll_data_dict.get('status', '')

    @property
    def poll_update_type(self):
        return self.data.message_dict.get('type', '')

    @property
    def is_poll_creation(self):
        return self.poll_update_type == 'POLL_CREATE'

    @property
    def is_poll_update(self):
        return self.poll_update_type == 'POLL_UPDATE'

    @property
    def is_poll_complete(self):
        return self.poll_update_type == 'POLL_COMPLETE'

    @property
    def is_poll_archive(self):
        return self.poll_update_type == 'POLL_ARCHIVE'

    @property
    def total_votes(self):
        return self.poll_data_dict.get('votes', {}).get('total', 0)

    @cached_property
    def choices(self) -> Union[Tuple, Tuple[TwitchPollVoteChoice, ...]]:
        choices = self.poll_data_dict.get('choices', None)
        if choices is None:
            return ()
        return tuple(map(TwitchPollVoteChoice, choices))

    @property
    def total_voters(self):
        return self.poll_data_dict.get('total_voters', -1)

    @property
    def status(self):
        return self.poll_data_dict.get('status', '')

    @property
    def ordered_choices(self) -> List[TwitchPollVoteChoice]:
        return sorted(self.choices, key=lambda c: c.total_votes, reverse=True)

    @property
    def remaining_milliseconds(self):
        return self.poll_data_dict.get('remaining_duration_milliseconds', 0)
