from datetime import datetime
from typing import NamedTuple

__all__ = ['Follower']


class Follower(NamedTuple):
    following_id: int
    following: str
    id: int
    name: str
    followed_at: datetime

    @property
    def is_valid(self):
        return bool(self.following_id) and bool(self.name.strip()) and bool(self.following.strip())
