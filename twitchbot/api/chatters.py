from dataclasses import dataclass

from ..exceptions import BadTwitchAPIResponse
from ..util import get_channel_chatters, CHANNEL_CHATTERS_URL

__all__ = [
    'Chatters',
    'CHANNEL_CHATTERS_URL'
]

MODERATORS = 'moderators'
STAFF = 'staff'
ADMINS = 'admins'
GLOBAL_MODS = 'global_mods'
VIEWERS = 'viewers'
CHATTER_COUNT = 'chatter_count'
CHATTERS = 'chatters'


@dataclass
class Chatters:
    channel: str
    mods: frozenset = frozenset()
    staff: frozenset = frozenset()
    admins: frozenset = frozenset()
    global_mods: frozenset = frozenset()
    viewers: frozenset = frozenset()
    all_viewers: frozenset = frozenset()
    viewer_count: int = 0

    async def update(self):
        json = ''
        try:
            json = await get_channel_chatters(self.channel)
            self._verify_base_response_is_valid(json)
            chatters = json['chatters']
            self._verify_chatters_response_is_valid(chatters)

            self.mods = frozenset(chatters[MODERATORS])
            self.staff = frozenset(chatters[STAFF])
            self.admins = frozenset(chatters[ADMINS])
            self.global_mods = frozenset(chatters[GLOBAL_MODS])
            self.viewers = frozenset(chatters[VIEWERS])
            self.viewer_count = json[CHATTER_COUNT]
            self.all_viewers = self.mods | self.staff | self.admins | self.global_mods | self.viewers | {self.channel}
        except Exception as e:
            print(f'\nCHATTERS API ERROR\njson received: {json}\n{e}\nEND CHATTERS API ERROR\n')

    def __contains__(self, item):
        return item.lower() in self.all_viewers

    def __iter__(self):
        yield from self.all_viewers

    def _verify_response_is_dict(self, json):
        if not isinstance(json, dict):
            raise BadTwitchAPIResponse(CHANNEL_CHATTERS_URL,
                                       f'response was not the expected type, expected: {dict}, actual: {type(json)}')

    def _verify_keys(self, json, keys):
        for key in keys:
            if key not in json:
                raise BadTwitchAPIResponse(CHANNEL_CHATTERS_URL, f'response is missing required key: {key}')

    def _verify_base_response_is_valid(self, json):
        self._verify_response_is_dict(json)
        self._verify_keys(json, (CHATTER_COUNT, CHATTERS))

    def _verify_chatters_response_is_valid(self, json):
        self._verify_response_is_dict(json)
        self._verify_keys(json, (MODERATORS, STAFF, ADMINS, GLOBAL_MODS, VIEWERS))
