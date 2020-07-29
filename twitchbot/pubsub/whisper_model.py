from typing import TYPE_CHECKING
from ..cached_property import cached_property

if TYPE_CHECKING:
    from twitchbot import PubSubData


class PubSubWhisper:
    def __init__(self, data: 'PubSubData'):
        self.data: 'PubSubData' = data

    @property
    def topic(self) -> str:
        return self.data.topic

    @property
    def id(self) -> str:
        return self.data.message_data.get('id', '')

    @property
    def last_read(self) -> int:
        return self.data.message_data.get('last_read', 0)

    @property
    def archived(self) -> bool:
        return self.data.message_data.get('archived', False)

    @property
    def is_muted(self) -> bool:
        return self.data.message_data.get('muted', False)

    @property
    def spam_likelihood(self) -> bool:
        return self.data.message_data.get('spam_info', {}).get('likelihood', False)

    @property
    def last_marked_not_spam(self) -> bool:
        return self.data.message_data.get('spam_info', {}).get('last_marked_not_spam', False)
