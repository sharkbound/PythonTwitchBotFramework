from typing import Optional

from .models import PubSubData
from ..util import dict_get_value, try_parse_json, get_channel_name_from_user_id
from ..cached_property import cached_property
from ..channel import channels, Channel

# example pubsub follow data
# {
#   'type': 'MESSAGE',
#   'data': {
#       'topic': 'following.ID_HERE',
#       'message': '{"display_name":"FOLLOWER","username":"FOLLOWER","user_id":"FOLLOWER_ID"}'
#   }
# }

__all__ = [
    'PubSubFollow'
]


class PubSubFollow:
    def __init__(self, data: PubSubData):
        self.data = data

    @property
    def topic(self):
        return dict_get_value(self.data.raw_data, 'data.topic', default='')

    @cached_property
    def data_message_dict(self):
        data = self.data.raw_data.get('data', {}).get('message', '')
        if isinstance(data, str):
            return try_parse_json(data)
        return data

    @property
    def follower_display_name(self) -> str:
        return self.data_message_dict.get('display_name', '')

    @property
    def follower_username(self) -> str:
        return self.data_message_dict.get('username', '')

    @property
    def follower_id(self) -> str:
        return self.data_message_dict.get('user_id', '')

    @property
    def channel_id(self) -> str:
        return self.topic.split('.')[1]

    async def get_channel(self) -> Optional[Channel]:
        name = (await get_channel_name_from_user_id(self.channel_id) or '').strip().lower()
        return channels.get(name)
