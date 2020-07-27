from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from twitchbot import PubSubData


class PubSubPointRedemption:
    def __init__(self, data: 'PubSubData'):
        self.data: 'PubSubData' = data

    @property
    def id(self):
        return self.data.channel_point_redemption_dict.get('id', '')

    @cached_property
    def user_dict(self):
        return self.data.channel_point_redemption_dict.get('user', {})

    @property
    def user_id(self):
        return self.user_dict.get('id', '')

    @property
    def user_login_name(self):
        return self.user_dict.get('login', '')

    @property
    def user_display_name(self):
        return self.user_dict.get('display_name', '')

    @property
    def channel_id(self):
        return self.data.channel_point_redemption_dict.get('channel_id', '')
