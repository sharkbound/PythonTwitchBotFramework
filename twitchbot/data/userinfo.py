from typing import NamedTuple

__all__ = ['UserInfo']


class UserInfo(NamedTuple):
    id: int
    login: str
    display_name: str
    type: str
    broadcaster_type: str
    description: str
    profile_image_url: str
    offline_image_url: str
    view_count: int
