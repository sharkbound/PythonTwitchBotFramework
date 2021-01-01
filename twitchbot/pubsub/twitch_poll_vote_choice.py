from ..util import dict_get_value

__all__ = [
    'TwitchPollVoteChoice'
]


class TwitchPollVoteChoice:
    def __init__(self, choice: dict):
        self._raw_choice = choice
        self.total_votes = dict_get_value(choice, 'votes.total', default=-1)
        self.bit_votes = dict_get_value(choice, 'votes.bits', default=-1)
        self.channel_points_votes = dict_get_value(choice, 'votes.channel_points', default=-1)
        self.base_votes = dict_get_value(choice, 'votes.base', default=-1)
        self.title = choice.get('title', '')
        self.choice_id = choice.get('choice_id', '')

    def __repr__(self):
        return f'<{self.__class__.__name__} title={self.title}, total_votes={self.total_votes}>'
