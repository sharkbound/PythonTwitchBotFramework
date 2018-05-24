from enum import Enum, IntFlag, auto


class NamedEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class UserType(NamedEnum):
    GLOBAL_MOD = auto()
    ADMIN = auto()
    STAFF = auto()
    AFFILIATE = auto()
    NORMAL = auto()


class MessageType(NamedEnum):
    PRIVMSG = auto()
    WHISPER = auto()
    COMMAND = auto()
    PING = auto()
    JOINED_CHANNEL = auto()
    NONE = auto()


class CommandContext(IntFlag):
    CHANNEL = auto()
    WHISPER = auto()
    BOTH = CHANNEL | WHISPER
