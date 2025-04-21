from dataclasses import dataclass
from enum import Enum


class EventSubMessageType(Enum):
    NOT_SET = "not_set"
    WELCOME = "welcome"



@dataclass
class PubSubMessage:
    raw_message: str


@dataclass
class EventSubWelcomeMessage(PubSubMessage):
    session_id: str
