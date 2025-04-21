from dataclasses import dataclass


@dataclass
class EventSubTopic:
    pass

@dataclass
class EventSubModeratorTopic(EventSubTopic):
    action: str
    initiating_user: int