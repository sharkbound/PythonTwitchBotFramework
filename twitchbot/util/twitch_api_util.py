from datetime import datetime
from typing import Dict, Tuple

from aiohttp import ClientSession, ClientResponse
from async_timeout import timeout

from ..config import cfg
from ..data import UserFollowers, UserInfo, RateLimit

__all__ = ('CHANNEL_CHATTERS_URL', 'get_channel_chatters', 'get_stream_data', 'get_url', 'get_user_data', 'get_user_id',
           'STREAM_API_URL', 'USER_API_URL', 'get_user_followers', 'USER_FOLLOWERS_API_URL', 'get_headers',
           'get_user_info', 'get_user_creation_date', 'USER_ACCOUNT_AGE_API')

USER_API_URL = 'https://api.twitch.tv/helix/users?login={}'
STREAM_API_URL = 'https://api.twitch.tv/helix/streams?user_login={}'
CHANNEL_CHATTERS_URL = 'https://tmi.twitch.tv/group/user/{}/chatters'
USER_FOLLOWERS_API_URL = 'https://api.twitch.tv/helix/users/follows?to_id={}'
USER_ACCOUNT_AGE_API = 'https://api.twitch.tv/kraken/users/{}'

user_id_cache: Dict[str, int] = {}


async def get_url(url: str, headers: dict = None) -> Tuple[ClientResponse, dict]:
    headers = headers or get_headers()
    async with ClientSession(headers=headers) as session:
        async with timeout(10):
            async with session.get(url) as resp:
                return resp, await resp.json()


async def get_user_info(user: str) -> UserInfo:
    _, json = await get_url(USER_API_URL.format(user), get_headers())

    if 'error' in json or not json.get('data', None):
        return UserInfo(-1, '', '', '', '', '', '', '', -1)

    data = json['data'][0]
    return UserInfo(
        id=int(data['id']),
        login=data['login'],
        display_name=data['display_name'],
        type=data['type'],
        broadcaster_type=data['broadcaster_type'],
        description=data['description'],
        profile_image_url=data['profile_image_url'],
        offline_image_url=data['offline_image_url'],
        view_count=data['view_count']
    )


async def get_user_creation_date(user: str) -> datetime:
    _, json = await get_url(USER_ACCOUNT_AGE_API.format(user), get_headers())

    if 'created_at' not in json:
        return datetime.min()
    #                                            2012-09-03T01:30:56Z
    return datetime.strptime(json['created_at'], '%Y-%m-%dT%H:%M:%SZ')


async def get_user_followers(user: str, headers: dict = None) -> UserFollowers:
    headers = headers or get_headers()
    user_id = await get_user_id(user, headers)
    _, json = await get_url(USER_FOLLOWERS_API_URL.format(user_id), get_headers())
    ratelimit = RateLimit.from_headers(_.headers)
    
    # covers invalid user id, or some other API error, such as invalid client-id
    if not json or json.get('status', -1) == 400:
        return UserFollowers(-1, '', -1, '', -1, [])

    return UserFollowers(follower_count=json['total'],
                         following=user,
                         following_id=user_id,
                         name=user,
                         id=user_id_cache[user],
                         followers=json['data'])


async def get_user_data(user: str, headers: dict = None) -> dict:
    headers = headers or get_headers()
    _, json = await get_url(USER_API_URL.format(user), headers)

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
    _, json = await get_url(STREAM_API_URL.format(user_id), headers)

    if not json.get('data'):
        return {}

    return json['data'][0]


async def get_channel_chatters(channel: str) -> dict:
    _, data = await get_url(CHANNEL_CHATTERS_URL.format(channel))
    return data


def get_headers():
    return {'Client-ID': cfg.client_id}
