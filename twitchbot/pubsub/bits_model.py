from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import PubSubData

from ..util import try_parse_json

__all__ = [
    'PubSubBits'
]

class PubSubBits:
    def __init__(self, raw: 'PubSubData'):
        self.data = raw

    @property
    def topic(self) -> str:
        return self.data.topic

    @property
    def username(self) -> str:
        return self.data.message_data.get('user_name', '') or ''

    @property
    def channel_name(self) -> str:
        return self.data.message_data.get('channel_name', '') or ''

    @property
    def channel_id(self) -> str:
        return self.data.message_data.get('channel_id', '') or ''

    @property
    def user_id(self) -> str:
        return self.data.message_data.get('user_id', '') or ''

    @property
    def chat_message(self) -> str:
        return self.data.message_data.get('chat_message', '')

    @property
    def bits_used(self) -> int:
        return self.data.message_data.get('bits_used', 0)

    @property
    def total_bits_used(self) -> int:
        return self.data.message_data.get('total_bits_used', 0)

    @property
    def is_anonymous(self) -> bool:
        return self.data.message_data.get('is_anonymous', False)

    @property
    def context(self) -> bool:
        return self.data.message_data.get('context', '')

    @property
    def badge_entitlement_dict(self) -> dict:
        return try_parse_json(self.data.message_data.get('badge_entitlement') or {})

    @property
    def version(self) -> str:
        return self.data.message_dict.get('version', '')

    @property
    def message_type(self) -> str:
        return self.data.message_dict.get('message_type', '')

    @property
    def message_id(self) -> str:
        return self.data.message_dict.get('message_id', '')
