from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import PubSubData

__all__ = [
    'PubSubSubscription'
]


# TODO
class PubSubSubscription:
    def __init__(self, raw: 'PubSubData'):
        self.data = raw
