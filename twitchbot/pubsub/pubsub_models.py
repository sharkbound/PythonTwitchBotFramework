import json

from ..util import dict_get_value
from functools import cached_property


class PubSubData:
    def __init__(self, raw_data: dict):
        self.raw_data: dict = raw_data

    @cached_property
    def topic(self) -> str:
        return dict_get_value(self.raw_data, 'data', 'topic', default='')

    @cached_property
    def message_dict(self):
        try:
            return json.loads(dict_get_value(self.raw_data, 'data', 'message'))
        except (TypeError, json.JSONDecodeError):
            return {}

    @cached_property
    def message_data(self):
        return self.message_dict.get('data', {})

    @cached_property
    def message_type_str(self) -> str:
        return self.message_data.get('type', '')

    @cached_property
    def message_type_str(self) -> str:
        return self.message_data.get('type', '')

    @cached_property
    def moderation_action_str(self) -> str:
        return self.message_data.get('moderation_action', '')
