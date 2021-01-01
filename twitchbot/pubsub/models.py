import json
from itertools import chain
from typing import TYPE_CHECKING

from ..util import dict_get_value, try_parse_json
from ..cached_property import cached_property

if TYPE_CHECKING:
    from .point_redemption_model import PubSubPointRedemption
    from .whisper_model import PubSubWhisper
    from .bits_model import PubSubBits
    from .pubsub_moderation_action import PubSubModerationAction
    from .subscription_model import PubSubSubscription
    from .pubsub_poll_update import PubSubPollData

__all__ = [
    'PubSubData'
]


class PubSubData:
    MESSAGE_TYPE = 'MESSAGE'
    RESPONSE_TYPE = 'RESPONSE'
    REWARD_REDEEMED_TYPE = 'reward-redeemed'
    WHISPER_MESSAGE_TYPE = 'thread'
    BITS_MESSAGE_TYPE = 'bits_event'
    SUBSCRIPTION_MESSAGE_TYPE = 'channel-subscribe-events-v1'

    def __init__(self, raw_data: dict):
        self.raw_data: dict = raw_data

    def as_point_redemption(self) -> 'PubSubPointRedemption':
        from .point_redemption_model import PubSubPointRedemption
        return PubSubPointRedemption(self)

    def as_whisper(self) -> 'PubSubWhisper':
        from .whisper_model import PubSubWhisper
        return PubSubWhisper(self)

    def as_moderation_action(self) -> 'PubSubModerationAction':
        from .pubsub_moderation_action import PubSubModerationAction
        return PubSubModerationAction(self)

    def as_bits(self) -> 'PubSubBits':
        from .bits_model import PubSubBits
        return PubSubBits(self)

    def as_subscription(self) -> 'PubSubSubscription':
        from .subscription_model import PubSubSubscription
        return PubSubSubscription(self)

    def as_twitch_poll_update(self) -> 'PubSubPollData':
        from .pubsub_poll_update import PubSubPollData
        return PubSubPollData(self)

    def is_type(self, type: str):
        return self.raw_data.get('type').lower() == type.lower()

    @property
    def is_message(self):
        return self.is_type(self.MESSAGE_TYPE)

    @cached_property
    def is_pong(self):
        return self.is_type('PONG')

    @property
    def is_whisper(self):
        return self.is_message and self.message_dict.get('type', '').lower() == self.WHISPER_MESSAGE_TYPE.lower()

    @property
    def is_response(self):
        return self.raw_data.get('type', '').lower() == self.RESPONSE_TYPE.lower()

    @cached_property
    def is_moderation_action(self) -> bool:
        return bool(self.message_data.get('moderation_action', ''))

    @property
    def is_channel_points_redeemed(self) -> bool:
        return self.is_type(self.MESSAGE_TYPE) and self.message_dict.get('type', '').lower() == self.REWARD_REDEEMED_TYPE.lower()

    @property
    def is_bits(self) -> bool:
        return self.is_type(self.MESSAGE_TYPE) and self.message_dict.get('message_type', '').lower() == self.BITS_MESSAGE_TYPE.lower()

    @property
    def is_subscription(self) -> bool:
        return self.is_type(self.MESSAGE_TYPE) and self.SUBSCRIPTION_MESSAGE_TYPE.lower() in self.topic.lower()

    @property
    def is_twitch_poll_update(self) -> bool:
        return 'poll_' in self.message_dict.get('type', '').lower()

    @property
    def has_message(self):
        return self.is_type(self.MESSAGE_TYPE) and dict_get_value(self.raw_data, 'data', 'message')

    @cached_property
    def channel_point_redemption_dict(self) -> dict:
        return self.message_data.get('redemption', {})

    @property
    def error(self) -> str:
        return self.raw_data.get('error', '')

    @property
    def has_error(self) -> bool:
        return bool(self.error)

    @property
    def nonce(self) -> str:
        return self.raw_data.get('nonce', '')

    @cached_property
    def topic(self) -> str:
        return dict_get_value(self.raw_data, 'data', 'topic', default='')

    @cached_property
    def message_dict(self):
        return try_parse_json(dict_get_value(self.raw_data, 'data', 'message', default='{}'))

    @cached_property
    def message_data(self) -> dict:
        data = self.message_dict.get('data', {})
        if isinstance(data, str):
            return try_parse_json(data)
        return data

    @cached_property
    def message_type(self) -> str:
        if self.is_whisper or self.is_channel_points_redeemed:
            return self.message_dict.get('type', '')
        try:
            return self.message_data.get('type', '')
        except AttributeError:
            return ''

    @cached_property
    def moderation_action(self) -> str:
        return self.message_data.get('moderation_action', '')

    @cached_property
    def args(self) -> list:
        return list(chain.from_iterable(arg.split() for arg in self.message_data.get('args', [])))

    @cached_property
    def created_by(self) -> str:
        return self.message_data.get('created_by', '')

    @cached_property
    def created_by_user_id(self) -> str:
        return self.message_data.get('created_by_user_id', '')

    @cached_property
    def msg_id(self) -> str:
        return self.message_data.get('msg_id', '')

    @cached_property
    def target_user_id(self) -> str:
        return self.message_data.get('target_user_id', '')

    @cached_property
    def target_user_login(self) -> str:
        return self.message_data.get('target_user_login', '')

    @cached_property
    def from_automod(self) -> bool:
        return self.message_data.get('from_automod', False)
