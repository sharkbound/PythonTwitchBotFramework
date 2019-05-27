from typing import NamedTuple


class Follower(NamedTuple):
    following_id: int
    following: str
    id: int
    name: str
