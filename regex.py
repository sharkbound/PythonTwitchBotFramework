import re

RE_PRIVMSG = re.compile(
    r':(?P<user>[\w\d]+)!(?P=user)@(?P=user)\.tmi\.twitch\.tv PRIVMSG #(?P<channel>[\w\d]+) :(?P<content>.+)')

# example WHISPER
# :userman2!userman2@userman2.tmi.twitch.tv WHISPER hammerheadb0t :hello world!
RE_WHISPER = re.compile(
    r':(?P<user>[\w\d]+)!(?P=user)@(?P=user)\.tmi\.twitch\.tv WHISPER (?P<receiver>[\w\d]+) :(?P<content>.+)')
