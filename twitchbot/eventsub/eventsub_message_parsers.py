import json
from typing import Optional

from .eventsub_message_types import EventSubMessage, EventSubWelcomeMessage, EventSubMessageType


def get_eventsub_message_type_str(json_data: dict) -> Optional[str]:
    if not isinstance(json_data, dict):
        return None

    metadata = json_data.get('metadata', {})
    if not isinstance(metadata, dict):
        return None

    return metadata.get('message_type')


def parse_eventsub_json(json_data: str) -> Optional[EventSubMessage]:
    try:
        parsed = json.loads(json_data)  # todo: fix type error: "TypeError: the JSON object must be str, bytes or bytearray, not NoneType"
    except json.JSONDecodeError:
        return None

    message_type = get_eventsub_message_type_str(parsed)
    if message_type is None:
        return EventSubMessage(parsed, message_type=EventSubMessageType.NOT_SET)

    if message_type == "session_welcome":
        return EventSubWelcomeMessage.from_json(parsed)

    return EventSubMessage(parsed, message_type=EventSubMessageType.NOT_SET)
