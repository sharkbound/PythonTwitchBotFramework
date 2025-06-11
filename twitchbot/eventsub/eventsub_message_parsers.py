import json
from typing import Optional

from .eventsub_message_types import (
    EventSubMessage,
    EventSubWelcomeMessage,
    EventSubMessageType,
    EventSubSessionReconnectMessage,
    EventSubSessionKeepaliveMessage,
    EventSubNotificationMessage,
    EventSubRevocationMessage,
)


def get_eventsub_message_type_str(json_data: dict) -> Optional[str]:
    if not isinstance(json_data, dict):
        return None

    metadata = json_data.get("metadata", {})
    if not isinstance(metadata, dict):
        return None

    return metadata.get("message_type")


def parse_eventsub_json(json_data: Optional[str]) -> Optional[EventSubMessage]:
    if json_data is None:
        return None

    try:
        parsed = json.loads(json_data)
    except (json.JSONDecodeError, TypeError):
        return None

    message_type = get_eventsub_message_type_str(parsed)
    if message_type is None:
        return EventSubMessage(parsed, message_type=EventSubMessageType.UNKNOWN)

    if message_type == "session_welcome":
        return EventSubWelcomeMessage.from_json(parsed)

    if message_type == "session_keepalive":
        return EventSubSessionKeepaliveMessage.from_json(parsed)

    if message_type == "notification":
        return EventSubNotificationMessage.from_json(parsed)

    if message_type == "session_reconnect":
        return EventSubSessionReconnectMessage.from_json(parsed)

    if message_type == "revocation":
        return EventSubRevocationMessage.from_json(parsed)

    return EventSubMessage.from_json(parsed)
