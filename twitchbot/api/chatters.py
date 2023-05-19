import traceback
from dataclasses import dataclass

from ..exceptions import BadTwitchAPIResponse
from ..util import get_channel_chatters, CHANNEL_CHATTERS_API_URL

__all__ = [
    'Chatters',
    'CHANNEL_CHATTERS_API_URL'
]

CHATTER_COUNT = 'total'
DATA = 'data'


@dataclass
class Chatters:
    channel: str
    viewers: frozenset = frozenset()
    viewer_count: int = 0

    async def update(self):
        json = ''
        try:
            json = await get_channel_chatters(self.channel)
            self._verify_base_response_is_valid(json)

            self.viewers = frozenset([viewer['user_login'] for viewer in json[DATA]])
            self.viewer_count = json[CHATTER_COUNT]
        except Exception as e:
            # twitch seems to have removed the chatters from the response from the API for some reason
            # don't want to spam the user with this error again and again, so until a better solution is found for 
            # tracking viewers for the loyalty ticker, just pass for now.
            pass
            print(f'\nCHATTERS API ERROR\n')
            print(f'json received: {json}\nexception ({type(e)}): {e}\n')
            print(f'stack trace:\n{traceback.format_exc()}')
            print('END CHATTERS API ERROR\n')

    def __contains__(self, item):
        return item.casefold() in self.viewers

    def __iter__(self):
        yield from self.viewers

    def _verify_response_is_dict(self, json):
        if not isinstance(json, dict):
            raise BadTwitchAPIResponse(CHANNEL_CHATTERS_API_URL,
                                       f'response was not the expected type, expected: {dict}, actual: {type(json)}'
                                       f'\nvalue: {json}')

    def _verify_keys(self, json, keys):
        for key in keys:
            if key not in json:
                raise BadTwitchAPIResponse(CHANNEL_CHATTERS_API_URL, f'response is missing required key: {key}')

    def _verify_base_response_is_valid(self, json):
        self._verify_response_is_dict(json)
        self._verify_keys(json, (CHATTER_COUNT, DATA))
