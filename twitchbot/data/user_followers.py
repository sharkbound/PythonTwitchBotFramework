from typing import List
from .follower import Follower

__all__ = ['UserFollowers']


class UserFollowers:
    __slots__ = ['followers', 'id', 'name', 'follower_count']

    def __init__(self, follower_count: int, following: str, following_id: int, name: str, id: int,
                 followers: List[dict]):
        self.followers: List[Follower] = [
            Follower(following=following,
                     following_id=int(following_id),
                     id=int(json['from_id']),
                     name=json['from_name'])
            for json in followers
            if 'from_id' in json and 'from_name' in json
        ]
        self.id: int = id
        self.name: str = name
        self.follower_count = follower_count

    def __iter__(self):
        yield from self.followers
