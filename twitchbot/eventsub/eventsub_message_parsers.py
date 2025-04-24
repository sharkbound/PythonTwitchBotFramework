import json
from typing import Optional

from .eventsub_message_types import EventSubMessage, parse_twitch_timestamp, EventSubWelcomeMessage, EventSubMessageType


def parse_eventsub_json(json_data: str) -> Optional[EventSubMessage]:
    try:
        parsed = json.loads(json_data)
    except json.JSONDecodeError:
        return None

    metadata = parsed.get('metadata', {})
    if metadata is None:
        return EventSubMessage(parsed, message_type=EventSubMessageType.NOT_SET)

    message_type = metadata.get('message_type')
    if message_type is None:
        return EventSubMessage(parsed, message_type=EventSubMessageType.NOT_SET)

    if message_type == "session_welcome":
        return EventSubWelcomeMessage.from_json(parsed)

    return EventSubMessage(parsed, message_type=EventSubMessageType.NOT_SET)
