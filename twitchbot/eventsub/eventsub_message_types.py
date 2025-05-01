from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class EventSubMessageType(Enum):
    NOT_SET = "not_set"
    WELCOME = "session_welcome"


def parse_twitch_timestamp(timestamp: str) -> datetime:
    # Remove the trailing 'Z' if it exists
    if timestamp.endswith('Z'):
        timestamp = timestamp[:-1]

    # Split timestamp into main part and fractional part
    if '.' in timestamp:
        parts = timestamp.split('.', 1)
        main_part = parts[0]
        fractional_part = parts[1]
        # Truncate fractional part to 6 digits (microseconds)
        fractional_part = fractional_part[:6]
        timestamp = f"{main_part}.{fractional_part}"
        # Use the format with microseconds
        dt_format = "%Y-%m-%dT%H:%M:%S.%f"
    else:
        # If there's no fractional part, use the format without it
        dt_format = "%Y-%m-%dT%H:%M:%S"

    return datetime.strptime(timestamp, dt_format)


def json_get_path(json_obj: dict, *key_path):
    for key in key_path:
        if isinstance(key, str) and isinstance(json_obj, dict):
            if key in json_obj:
                json_obj = json_obj[key]
            else:
                return None

        elif isinstance(key, int) and isinstance(json_obj, list):
            if 0 <= key < len(json_obj):
                json_obj = json_obj[key]
            else:
                return None

    return json_obj


@dataclass
class EventSubMessage:
    raw_data: dict
    message_type: EventSubMessageType

    def as_welcome_message(self) -> Optional['EventSubWelcomeMessage']:
        if self.message_type is not EventSubMessageType.WELCOME:
            return None
        return self


@dataclass
class EventSubWelcomeMessage(EventSubMessage):
    message_id: str
    session_id: str
    message_type_str: str
    message_timestamp: datetime
    session_id: str
    session_status: str
    connected_at: datetime
    keepalive_timeout_seconds: int
    reconnect_url: str
    recovery_url: str

    @staticmethod
    def from_json(json_data: dict) -> Optional['EventSubWelcomeMessage']:
        if json_get_path(json_data, 'metadata', 'message_type') != 'session_welcome':
            return None

        return EventSubWelcomeMessage(
            message_id=json_get_path(json_data, 'metadata', 'message_id'),
            message_type_str=json_get_path(json_data, 'metadata', 'message_type'),
            message_timestamp=parse_twitch_timestamp(json_get_path(json_data, 'metadata', 'message_timestamp')),
            session_id=json_get_path(json_data, 'payload', 'session', 'id'),
            session_status=json_get_path(json_data, 'payload', 'session', 'status'),
            connected_at=parse_twitch_timestamp(json_get_path(json_data, 'payload', 'session', 'connected_at')),
            keepalive_timeout_seconds=int(json_get_path(json_data, 'payload', 'session', 'keepalive_timeout_seconds')),
            reconnect_url=json_get_path(json_data, 'payload', 'session', 'reconnect_url'),
            recovery_url=json_get_path(json_data, 'payload', 'session', 'recovery_url'),
            raw_data=json_data,
            message_type=EventSubMessageType.WELCOME,
        )
