from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Hashable, Optional, Union

__all__ = [
    'CooldownManager'
]


class CooldownManager:
    def __init__(self):
        self._cooldowns: Dict[Hashable, datetime] = {}

    def remove_cooldown(self, key: Hashable):
        if key in self._cooldowns:
            del self._cooldowns[key]

    def set_cooldown(self, key: Hashable, value: Optional[datetime] = None):
        self._cooldowns[key] = value if value is not None else datetime.now()

    def diff_delta(self, key: Hashable) -> timedelta:
        return datetime.now() - self.get(key, datetime.min)

    def on_cooldown(self, key: Hashable, required_min_seconds: Union[int, float, Decimal]) -> bool:
        if key not in self:
            return False
        else:
            return self.elapsed_seconds(key) < required_min_seconds

    def seconds_left(self, key: Hashable, required_min_seconds: Union[int, float, Decimal]):
        return required_min_seconds - (datetime.now() - self.get(key, datetime.now())).total_seconds()

    def elapsed_seconds(self, key: Hashable) -> float:
        if key not in self:
            return 0
        return abs(self.diff_delta(key).total_seconds())

    def get(self, key: Hashable, default=None):
        return self._cooldowns.get(key, default)

    def __getitem__(self, item: Hashable) -> datetime:
        return self._cooldowns[item]

    def __contains__(self, item: Hashable):
        return item in self._cooldowns
