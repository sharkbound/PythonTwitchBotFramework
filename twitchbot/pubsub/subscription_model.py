from typing import TYPE_CHECKING
from ..cached_property import cached_property

if TYPE_CHECKING:
    from .models import PubSubData

__all__ = [
    'PubSubSubscription'
]


class PubSubSubscription:
    def __init__(self, raw: 'PubSubData'):
        self.data = raw

    @property
    def topic(self) -> str:
        return self.data.topic

    @property
    def benefit_end_month(self) -> int:
        return self.data.message_dict.get('benefit_end_month', -1)

    @property
    def channel_id(self) -> str:
        return self.data.message_dict.get('channel_id', '')

    @property
    def channel_name(self) -> str:
        return self.data.message_dict.get('channel_name', '')

    @property
    def context(self) -> str:
        return self.data.message_dict.get('context', '')

    @property
    def cumulative_months(self) -> int:
        return self.data.message_dict.get('cumulative_months', 0)

    @property
    def display_name(self) -> str:
        return self.data.message_dict.get('display_name', '')

    @property
    def is_gift(self) -> bool:
        return self.data.message_dict.get('is_gift', False)

    @property
    def months(self) -> int:
        return self.data.message_dict.get('months', 0)

    @property
    def multi_month_duration(self) -> int:
        return self.data.message_dict.get('multi_month_duration', 0)

    @property
    def streak_months(self) -> int:
        return self.data.message_dict.get('streak_months', 0)

    @cached_property
    def sub_message_dict(self) -> dict:
        return self.data.message_dict.get('sub_message', {}) or {}

    @property
    def sub_plan(self) -> str:
        return self.data.message_dict.get('sub_plan', '')

    @property
    def sub_plan_name(self) -> str:
        return self.data.message_dict.get('sub_plan_name', '')

    @property
    def user_id(self) -> str:
        return self.data.message_dict.get('user_id', '')

    @property
    def user_name(self) -> str:
        return self.data.message_dict.get('user_name', '')
