from typing import Dict
from dataclasses import dataclass, field
from .util import get_url


@dataclass(frozen=True)
class Emote:
    id: int
    code: str
    set: int = field(default=0, repr=False)


GLOBAL_EMOTE_API = 'https://api.twitchemotes.com/api/v4/channels/0'
emotes: Dict[str, Emote] = {}


async def update_global_emotes():
    data = None
    # todo: find new url/api for fetching global emotes
    # _, data = await get_url(GLOBAL_EMOTE_API)

    if not data or 'emotes' not in data:
        return

    emotes.clear()
    for emote in data['emotes']:
        emotes[emote['code']] = Emote(int(emote['id']), emote['code'], emote['emoticon_set'])
