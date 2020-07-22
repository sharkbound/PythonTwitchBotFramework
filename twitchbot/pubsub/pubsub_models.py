from typing import Optional

from ..util import CachedProperty, dict_get_path

class PubSubData:
    def __init__(self, raw_data: dict):
        self.raw_data: dict = raw_data
        # todo

    @CachedProperty
    def topic(self) -> str:
        return dict_get_path(self.raw_data, '')





