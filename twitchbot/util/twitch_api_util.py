import warnings
from collections import namedtuple
from datetime import datetime
from json import JSONDecodeError
from typing import Dict, Tuple, NamedTuple, Optional

from aiohttp import ClientSession, ClientResponse, ContentTypeError
from async_timeout import timeout

from ..config import get_client_id, get_oauth, DEFAULT_CLIENT_ID
from ..data import UserFollowers, UserInfo, RateLimit

__all__ = ('CHANNEL_CHATTERS_URL', 'get_channel_chatters', 'get_stream_data', 'get_url', 'get_user_data', 'get_user_id',
           'STREAM_API_URL', 'USER_API_URL', 'get_user_followers', 'USER_FOLLOWERS_API_URL', 'get_headers',
           'get_user_info', 'get_user_creation_date', 'USER_ACCOUNT_AGE_API', 'CHANNEL_INFO_API', 'get_channel_info', 'ChannelInfo',
           'get_channel_name_from_user_id', 'OauthTokenInfo', 'get_oauth_token_info', '_check_token', 'post_url')

USER_API_URL = 'https://api.twitch.tv/helix/users?login={}'
STREAM_API_URL = 'https://api.twitch.tv/helix/streams?user_login={}'
CHANNEL_CHATTERS_URL = 'https://tmi.twitch.tv/group/user/{}/chatters'
USER_FOLLOWERS_API_URL = 'https://api.twitch.tv/helix/users/follows?to_id={}'
USER_ACCOUNT_AGE_API = 'https://api.twitch.tv/kraken/users/{}'
CHANNEL_INFO_API = 'https://api.twitch.tv/helix/channels?broadcaster_id={}'

user_id_cache: Dict[str, int] = {}


async def get_url(url: str, headers: dict = None) -> Tuple[ClientResponse, dict]:
    headers = headers or get_headers()
    async with ClientSession(headers=headers) as session:
        async with timeout(10):
            async with session.get(url) as resp:
                return await _extract_response_and_json_from_request(resp)


async def post_url(url: str, headers: dict = None) -> Tuple[ClientResponse, dict]:
    headers = headers or get_headers()
    async with ClientSession(headers=headers) as session:
        async with timeout(10):
            async with session.post(url) as resp:
                return await _extract_response_and_json_from_request(resp)


async def _extract_response_and_json_from_request(resp):
    try:
        return resp, await resp.json()
    except (ContentTypeError, JSONDecodeError, TypeError):
        return resp, {}


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
    _, json = await get_url(USER_ACCOUNT_AGE_API.format(user), get_headers(use_kraken=True))

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


async def get_user_id(user: str, headers: dict = None, verbose=True) -> int:
    headers = headers or get_headers()
    # shortcut if the this user's id was already requested
    if user in user_id_cache:
        return user_id_cache[user]

    data = await get_user_data(user, headers)

    if not data:
        if verbose:
            warnings.warn(f'[GET_USER_ID] unable to get user_id for username "{user}"')
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


def get_headers(use_kraken: bool = False):
    prefix = 'Bearer' if not use_kraken else 'OAuth'
    oauth_key = get_oauth(remove_prefix=True)
    headers = {'Client-ID': get_client_id()}
    if oauth_key:
        headers.update({'Authorization': f'{prefix} {oauth_key}'})

    return headers


ChannelInfo = NamedTuple(
    'ChannelInfo', (
        ('broadcaster_id', str),
        ('broadcaster_name', str),
        ('broadcaster_language', str),
        ('game_id', str),
        ('game_name', str),
        ('title', str))
)


async def get_channel_info(broadcaster_name_or_id: str, headers: dict = None) -> Optional[ChannelInfo]:
    from ..util import dict_get_value

    if not broadcaster_name_or_id.strip().isnumeric():
        user_id = await get_user_id(broadcaster_name_or_id, headers=headers)
        if user_id == -1:
            return None
    else:
        user_id = broadcaster_name_or_id

    _, json = await get_url(CHANNEL_INFO_API.format(user_id), headers=headers)
    data = dict_get_value(json, 'data', 0)

    if not data:
        return None

    return ChannelInfo(broadcaster_id=data['broadcaster_id'], broadcaster_name=data['broadcaster_name'],
                       broadcaster_language=data['broadcaster_language'], game_id=data['game_id'], game_name=data['game_name'], title=data['title'])


_channel_id_to_name_cache = {}


async def get_channel_name_from_user_id(user_id: str, headers: dict = None) -> str:
    user_id = user_id.strip()

    if user_id in _channel_id_to_name_cache:
        return _channel_id_to_name_cache[user_id]

    headers = headers or get_headers()
    channel_info = await get_channel_info(user_id, headers=headers)

    if not channel_info:
        return ''

    _channel_id_to_name_cache[user_id] = channel_info.broadcaster_name
    return channel_info.broadcaster_name


OauthTokenInfo = namedtuple('OauthTokenInfo', 'client_id login scopes user_id expires_in error_message status')


async def get_oauth_token_info(token: str) -> OauthTokenInfo:
    token = token.replace('oauth:', '')
    _, json = await get_url('https://id.twitch.tv/oauth2/validate', headers={'Authorization': f'OAuth {token}'})
    return OauthTokenInfo(client_id=json.get('client_id', ''),
                          login=json.get('login', ''),
                          scopes=json.get('scopes', []),
                          user_id=json.get('user_id', ''),
                          expires_in=json.get('expires_in', 0),
                          error_message=json.get('message', ''),
                          status=json.get('status', -1))


def _print_quit(msg):
    print(msg)
    input('\npress ENTER to exit...')
    exit(1)


def _check_token(info: OauthTokenInfo):
    if not info.login or info.status != -1:
        _print_quit(f'\nfailed to login to chat, irc oauth token is INVALID/EXPIRED ("oauth" in the config)\n'
                    f'twitch returned status code ({info.status}) and error message ({info.error_message})')

    if get_client_id() != DEFAULT_CLIENT_ID and info.client_id != get_client_id():
        print(f'\n{"=" * 50}\nthe client id for the irc oauth token ("oauth" in the config) DOES NOT match the client id in the config\n'
              f'TWITCH API CALLS WILL NOT WORK until the irc token is regenerated using the client id in the config\n'
              f'\nreplace the <CLIENT_ID_HERE> and <REDIRECT_HERE> in the following auth URL to match your twitch dev app info\nthen visit the URL with '
              f'a browser signed into the bots account to correct this problem\nmake sure to replace the current irc oauth token with the new one ("oauth" in config)'
              f'\n\nhttps://id.twitch.tv/oauth2/authorize?response_type=token&client_id=<CLIENT_ID_HERE>&redirect_uri=<REDIRECT_HERE>'
              f'&scope=chat:read+chat:edit+channel:moderate+whispers:read+whispers:edit+channel_editor'
              f'\n{"=" * 50}\n')

    print(f'logged into chat as "{info.login}"')
