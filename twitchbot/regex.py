import re

RE_PRIVMSG = re.compile(
    r'(?P<tags>.*):'
    r'(?P<user>[\w\d]+)!(?P=user)@(?P=user)\.tmi\.twitch\.tv PRIVMSG #(?P<channel>[\w\d]+) :(?P<content>.+)'
)

# example whisper
# :nickname!nickname@nickname.tmi.twitch.tv WHISPER bob :hello world!
RE_WHISPER = re.compile(
    r':(?P<user>[\w\d]+)!(?P=user)@(?P=user)\.tmi\.twitch\.tv WHISPER (?P<receiver>[\w\d]+) :(?P<content>.+)'
)

# example joining channel
# :nickname!nickname@nickname.tmi.twitch.tv JOIN #bob
RE_JOINED_CHANNEL = re.compile(
    r':(?P<user>[\w\d]+)!(?P=user)@(?P=user)\.tmi\.twitch\.tv JOIN #(?P<channel>\w+)'
)

# finds mentions in twitch messages
# example: hello @bob!
RE_AT_MENTION = re.compile(
    r'@([\w\d]+)'
)

# user notices / subscriptions
RE_USERNOTICE = re.compile(
    r'(?P<tags>.*):tmi\.twitch\.tv USERNOTICE #(?P<channel>[\w\d]+)( :)?(?P<content>.+)?'
)
