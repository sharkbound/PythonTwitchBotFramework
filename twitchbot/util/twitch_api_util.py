from typing import Dict

from aiohttp import ClientSession
from async_timeout import timeout
from ..data import UserFollowers, Follower
from ..config import cfg

__all__ = ('CHANNEL_CHATTERS_URL', 'get_channel_chatters', 'get_stream_data', 'get_url', 'get_user_data', 'get_user_id',
           'STREAM_API_URL', 'USER_API_URL', 'get_user_followers', 'USER_FOLLOWERS_API_URL', 'get_headers')

USER_API_URL = 'https://api.twitch.tv/helix/users?login={}'
STREAM_API_URL = 'https://api.twitch.tv/helix/streams?user_login={}'
CHANNEL_CHATTERS_URL = 'https://tmi.twitch.tv/group/user/{}/chatters'
USER_FOLLOWERS_API_URL = 'https://api.twitch.tv/helix/users/follows?to_id={}'

user_id_cache: Dict[str, int] = {}


async def get_url(url: str, headers: dict = None) -> dict:
    headers = headers or get_headers()
    async with ClientSession(headers=headers) as session:
        async with timeout(10):
            async with session.get(url) as resp:
                return await resp.json()


async def get_user_followers(user: str, headers: dict = None) -> UserFollowers:
    headers = headers or get_headers()
    user_id = await get_user_id(user, headers)
    json = await get_url(USER_FOLLOWERS_API_URL.format(user_id), get_headers())

    # covers invalid user id, or some other API error, such as invalid client-id
    if not json or json.get('status', -1) == 400:
        return UserFollowers('', -1, '', -1, [])

    return UserFollowers(follower_count=json['total'],
                         following=user,
                         following_id=user_id,
                         name=user,
                         id=user_id_cache[user],
                         followers=json['data'])


async def get_user_data(user: str, headers: dict = None) -> dict:
    headers = headers or get_headers()
    json = await get_url(USER_API_URL.format(user), headers)

    if not json.get('data'):
        return {}

    return json['data'][0]


async def get_user_id(user: str, headers: dict = None) -> int:
    headers = headers or get_headers()
    # shortcut if the this user's id was already requested
    if user in user_id_cache:
        return user_id_cache[user]

    data = await get_user_data(user, headers)

    if not data:
        return -1

    user_id_cache[user] = data['id']
    return data['id']


async def get_stream_data(user_id: str, headers: dict = None) -> dict:
    headers = headers or get_headers()
    json = await get_url(STREAM_API_URL.format(user_id), headers)

    if not json.get('data'):
        return {}

    return json['data'][0]


async def get_channel_chatters(channel: str) -> dict:
    return await get_url(CHANNEL_CHATTERS_URL.format(channel))


def get_headers():
    return {'Client-ID': cfg.client_id}
