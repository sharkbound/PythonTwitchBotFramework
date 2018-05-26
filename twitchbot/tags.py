import re


class Tags:
    def __init__(self, tags_str):
        self.all_tags = {name: value for name, value in _split_tags_str(tags_str)}
        self.badges: str = self.all_tags.get('@badges')
        self.color: str = self.all_tags.get('color')
        self.display_name: str = self.all_tags.get('display-name')
        self.emotes: str = self.all_tags.get('emotes')
        self.id: str = self.all_tags.get('id')
        self.mod: int = _try_parse_int(self.all_tags.get('mod'))
        self.room_id: int = _try_parse_int(self.all_tags.get('room-id'))
        self.subscriber: int = _try_parse_int(self.all_tags.get('subscriber'))
        self.tmi_sent_ts: int = _try_parse_int(self.all_tags.get('tmi-sent-ts'))
        self.turbo: int = _try_parse_int(self.all_tags.get('turbo'))
        self.user_id: int = _try_parse_int(self.all_tags.get('user-id'))
        self.user_type: int = self.all_tags.get('user-type')
        self.bits: int = _try_parse_int(self.all_tags.get('bits'))


def _split_tags_str(tags):
    for tag in tags.split(';'):
        name, _, value = tag.partition('=')
        yield name, value


def _try_parse_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# example tags (split by =)
# (('@badges', 'broadcaster/1'),
# ('color', '#FF69B4'),
# ('display-name', 'bob'),
# ('emotes', ''),
# ('id', '4585b203-ad2e-40ab-9a54-e4d6e91cb85e'),
# ('mod', '0'),
# ('room-id', '1234'),
# ('subscriber', '0'),
# ('tmi-sent-ts', '1527291908857'),
# ('turbo', '0'),
# ('user-id', '1234'),
# ('user-type', ' '))
