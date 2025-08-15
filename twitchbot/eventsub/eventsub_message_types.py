from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Union


def parse_twitch_timestamp(timestamp: str) -> datetime:
    # Remove the trailing 'Z' if it exists
    if timestamp.endswith("Z"):
        timestamp = timestamp[:-1]

    # Split timestamp into main part and fractional part
    if "." in timestamp:
        parts = timestamp.split(".", 1)
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
            if 0 <= key < len(json_obj) or -len(json_obj) <= key < 0:
                json_obj = json_obj[key]
            else:
                return None

    return json_obj


class EventSubMessageType(Enum):
    UNKNOWN = "UNKNOWN"
    SESSION_WELCOME = "session_welcome"
    SESSION_KEEPALIVE = "session_keepalive"
    SESSION_RECONNECT = "session_reconnect"
    NOTIFICATION = "notification"
    REVOCATION = "revocation"


GENERIC_MESSAGE_INPUT_DATA_TYPE = Optional[Union[dict, list, str, int, datetime]]


class EventSubGenericMessage:
    def __init__(self, json_data: GENERIC_MESSAGE_INPUT_DATA_TYPE):
        self._raw_value: GENERIC_MESSAGE_INPUT_DATA_TYPE = json_data

    def pretty_printed_str(self):
        import pprint

        if isinstance(self._raw_value, dict):
            return pprint.pformat(self._raw_value, indent=4)
        return "Cannot pretty print non-dict data. Expected dict. Got: {}".format(
            type(self._raw_value)
        )

    @classmethod
    def EMPTY(cls):
        if hasattr(cls, "_static_empty_instance"):
            return cls._static_empty_instance

        cls._static_empty_instance = cls(None)
        return cls._static_empty_instance

    @property
    def IS_EMPTY(self):
        return self is self.__class__.EMPTY()

    @property
    def current_value(self):
        return self._raw_value

    def get(self, key: Union[str, int], default=None):
        """
        Gets the raw value of the current value using the provided key.
        Returns `default` if the key is missing, not found, or is out of range of the object this `GenericMessage` has.
        The default parameter is set to `None`, unless another value is specified.
        """
        if isinstance(key, str) and isinstance(self._raw_value, dict):
            return self._raw_value.get(key, default)

        if isinstance(key, int) and isinstance(self._raw_value, list):
            if 0 <= key < len(self._raw_value) or -len(self._raw_value) <= key < 0:
                return self._raw_value[key]

        return default

    def current_value_or_none(self):
        if self.IS_EMPTY:
            return None

        return self._raw_value

    def current_value_or(self, default=None):
        if self.IS_EMPTY:
            return default

        return self._raw_value

    def __getattr__(self, item):
        if self.IS_EMPTY:
            return self

        val = None
        if item in self.__dict__:
            val = self.__dict__[item]
        elif item in self._raw_value:
            val = self._raw_value[item]

        return self.EMPTY() if val is None else EventSubGenericMessage(val)

    def __getitem__(self, item):
        if self.IS_EMPTY:
            return self

        if isinstance(item, str) and isinstance(self._raw_value, dict):
            if item in self._raw_value:
                return EventSubGenericMessage(self._raw_value[item])
            return self.__class__.EMPTY()

        if isinstance(item, int) and isinstance(self._raw_value, list):
            if 0 <= item < len(self._raw_value) or -len(self._raw_value) <= item < 0:
                return EventSubGenericMessage(self._raw_value[item])
            return self.__class__.EMPTY()

        return self.__class__.EMPTY()


@dataclass
class EventSubMessage:
    raw_data: dict
    message_type: EventSubMessageType

    @property
    def message_id(self) -> Optional[str]:
        return json_get_path(self.raw_data, "metadata", "message_id")

    def channel_name(self) -> Optional[str]:
        # Prefer login (lowercase) when available; fall back to display name.
        # Use the subscription condition to disambiguate events that include
        # both "from_" and "to_" broadcasters (e.g., raids, shoutouts).
        event = json_get_path(self.raw_data, "payload", "event")
        if not isinstance(event, dict):
            return None

        condition = json_get_path(
            self.raw_data, "payload", "subscription", "condition"
        )

        def first_in_event(*keys: str) -> Optional[str]:
            for k in keys:
                v = json_get_path(event, k)
                if isinstance(v, str) and v:
                    return v
            return None

        if isinstance(condition, dict):
            key_map = [
                (
                    "broadcaster_user_id",
                    (
                        "broadcaster_user_login",
                        "broadcaster_login",
                        "broadcaster_user_name",
                        "broadcaster_name",
                    ),
                ),
                (
                    "to_broadcaster_user_id",
                    ("to_broadcaster_user_login", "to_broadcaster_user_name"),
                ),
                (
                    "from_broadcaster_user_id",
                    ("from_broadcaster_user_login", "from_broadcaster_user_name"),
                ),
                (
                    "host_broadcaster_user_id",
                    ("host_broadcaster_user_login", "host_broadcaster_user_name"),
                ),
                (
                    "source_broadcaster_user_id",
                    (
                        "source_broadcaster_user_login",
                        "source_broadcaster_user_name",
                    ),
                ),
            ]

            for cond_key, login_keys in key_map:
                if cond_key in condition:
                    val = first_in_event(*login_keys)
                    if val:
                        return val

        # Fallbacks cover most notification types, including chat events,
        # raids/shoutouts (from/to/host/source), and user-scoped events.
        return first_in_event(
            "broadcaster_user_login",
            "broadcaster_login",
            "from_broadcaster_user_login",
            "to_broadcaster_user_login",
            "host_broadcaster_user_login",
            "source_broadcaster_user_login",
            "broadcaster_user_name",
            "broadcaster_name",
            "from_broadcaster_user_name",
            "to_broadcaster_user_name",
            "host_broadcaster_user_name",
            "source_broadcaster_user_name",
            "user_login",
            "user_name",
        )

    @property
    def message_timestamp(self) -> Optional[datetime]:
        timestamp = json_get_path(self.raw_data, "metadata", "message_timestamp")
        if timestamp is not None:
            return parse_twitch_timestamp(timestamp)
        return None

    def message_type_str(self) -> Optional[str]:
        return json_get_path(self.raw_data, "metadata", "message_type")

    def as_generic(self) -> "EventSubGenericMessage":
        return EventSubGenericMessage(self.raw_data)

    def as_welcome_message(self) -> Optional["EventSubWelcomeMessage"]:
        if self.message_type is not EventSubMessageType.SESSION_WELCOME:
            return None
        return self

    def as_keepalive_message(self) -> Optional["EventSubSessionKeepaliveMessage"]:
        if self.message_type is not EventSubMessageType.SESSION_KEEPALIVE:
            return None
        return self

    def as_reconnect_message(self) -> Optional["EventSubSessionReconnectMessage"]:
        if self.message_type is not EventSubMessageType.SESSION_RECONNECT:
            return None
        return self

    def as_notification_message(self) -> Optional["EventSubNotificationMessage"]:
        if self.message_type is not EventSubMessageType.NOTIFICATION:
            return None
        return self

    def as_revocation_message(self) -> Optional["EventSubRevocationMessage"]:
        if self.message_type is not EventSubMessageType.REVOCATION:
            return None
        return self

    @classmethod
    def from_json(cls, json_data: dict) -> Optional["EventSubMessage"]:
        message_type = json_get_path(json_data, "metadata", "message_type")
        if message_type is None:
            return EventSubMessage(json_data, EventSubMessageType.UNKNOWN)

        if message_type == "session_welcome":
            return cls(json_data, message_type=EventSubMessageType.SESSION_WELCOME)

        if message_type == "session_keepalive":
            return cls(json_data, message_type=EventSubMessageType.SESSION_KEEPALIVE)

        if message_type == "session_reconnect":
            return cls(json_data, message_type=EventSubMessageType.SESSION_RECONNECT)

        if message_type == "notification":
            return cls(json_data, message_type=EventSubMessageType.NOTIFICATION)

        return cls(json_data, message_type=EventSubMessageType.UNKNOWN)


@dataclass
class EventSubWelcomeMessage(EventSubMessage):
    session_id: str
    session_id: str
    session_status: str
    connected_at: datetime
    keepalive_timeout_seconds: int
    reconnect_url: str
    recovery_url: str

    @classmethod
    def from_json(cls, json_data: dict) -> Optional["EventSubWelcomeMessage"]:
        if json_get_path(json_data, "metadata", "message_type") != "session_welcome":
            return None

        return cls(
            session_id=json_get_path(json_data, "payload", "session", "id"),
            session_status=json_get_path(json_data, "payload", "session", "status"),
            connected_at=parse_twitch_timestamp(
                json_get_path(json_data, "payload", "session", "connected_at")
            ),
            keepalive_timeout_seconds=int(
                json_get_path(
                    json_data, "payload", "session", "keepalive_timeout_seconds"
                )
            ),
            reconnect_url=json_get_path(
                json_data, "payload", "session", "reconnect_url"
            ),
            recovery_url=json_get_path(json_data, "payload", "session", "recovery_url"),
            raw_data=json_data,
            message_type=EventSubMessageType.SESSION_WELCOME,
        )


@dataclass
class EventSubSessionKeepaliveMessage(EventSubMessage):
    @classmethod
    def from_json(cls, json_data: dict) -> Optional["EventSubSessionKeepaliveMessage"]:
        if json_get_path(json_data, "metadata", "message_type") != "session_keepalive":
            return None

        return cls(
            raw_data=json_data,
            message_type=EventSubMessageType.SESSION_KEEPALIVE,
        )


@dataclass
class EventSubSessionReconnectMessage(EventSubMessage):
    session_id: str
    session_status: str
    keepalive_timeout_seconds: Optional[int]
    reconnect_url: str
    connected_at: datetime

    @classmethod
    def from_json(cls, json_data: dict) -> Optional["EventSubSessionReconnectMessage"]:
        if json_get_path(json_data, "metadata", "message_type") != "session_reconnect":
            return None

        return cls(
            session_id=json_get_path(json_data, "payload", "session", "id"),
            session_status=json_get_path(json_data, "payload", "session", "status"),
            keepalive_timeout_seconds=json_get_path(
                json_data, "payload", "session", "keepalive_timeout_seconds"
            ),
            reconnect_url=json_get_path(
                json_data, "payload", "session", "reconnect_url"
            ),
            connected_at=parse_twitch_timestamp(
                json_get_path(json_data, "payload", "session", "connected_at")
            ),
            raw_data=json_data,
            message_type=EventSubMessageType.SESSION_RECONNECT,
        )


@dataclass
class EventSubNotificationMessage(EventSubMessage):
    subscription_type_str: str
    subscription_version: str
    subscription_broadcaster_user_id: str
    subscription_moderator_user_id: str
    subscription_cost: int
    subscription_created_at: datetime
    subscription_id: str
    subscription_status: str
    subscription_transport_method: str
    subscription_transport_session_id: str

    def payload(self) -> Optional[dict]:
        return json_get_path(self.raw_data, "payload")

    def payload_as_generic(self) -> "EventSubGenericMessage":
        return EventSubGenericMessage(self.payload())

    @classmethod
    def from_json(cls, json_data: dict) -> Optional["EventSubNotificationMessage"]:
        if json_get_path(json_data, "metadata", "message_type") != "notification":
            return None

        return cls(
            raw_data=json_data,
            # Metadata
            message_type=EventSubMessageType.NOTIFICATION,
            subscription_type_str=json_get_path(
                json_data, "metadata", "subscription_type"
            ),
            subscription_version=json_get_path(
                json_data, "metadata", "subscription_version"
            ),
            # Subscription
            subscription_broadcaster_user_id=json_get_path(
                json_data, "payload", "subscription", "condition", "broadcaster_user_id"
            ),
            subscription_moderator_user_id=json_get_path(
                json_data, "payload", "subscription", "condition", "moderator_user_id"
            ),
            subscription_cost=int(
                json_get_path(json_data, "payload", "subscription", "cost")
            ),
            subscription_created_at=parse_twitch_timestamp(
                json_get_path(json_data, "payload", "subscription", "created_at")
            ),
            subscription_id=json_get_path(json_data, "payload", "subscription", "id"),
            subscription_status=json_get_path(
                json_data, "payload", "subscription", "status"
            ),
            subscription_transport_method=json_get_path(
                json_data, "payload", "subscription", "transport", "method"
            ),
            subscription_transport_session_id=json_get_path(
                json_data, "payload", "subscription", "transport", "session_id"
            ),
        )


@dataclass
class EventSubRevocationMessage(EventSubMessage):
    subscription_id: str
    subscription_status: str
    subscription_cost: int
    subscription_type_str: str
    subscription_version: str
    subscription_broadcaster_user_id: str
    subscription_transport_method: str
    subscription_transport_session_id: str
    subscription_created_at: datetime

    @classmethod
    def from_json(cls, json_data: dict) -> Optional["EventSubRevocationMessage"]:
        if json_get_path(json_data, "metadata", "message_type") != "revocation":
            return None

        return cls(
            raw_data=json_data,
            # Metadata
            message_type=EventSubMessageType.REVOCATION,
            subscription_type_str=json_get_path(
                json_data, "metadata", "subscription_type"
            ),
            subscription_version=json_get_path(
                json_data, "metadata", "subscription_version"
            ),
            subscription_broadcaster_user_id=json_get_path(
                json_data, "payload", "subscription", "condition", "broadcaster_user_id"
            ),
            subscription_cost=int(
                json_get_path(json_data, "payload", "subscription", "cost")
            ),
            subscription_created_at=parse_twitch_timestamp(
                json_get_path(json_data, "payload", "subscription", "created_at")
            ),
            subscription_id=json_get_path(json_data, "payload", "subscription", "id"),
            subscription_status=json_get_path(
                json_data, "payload", "subscription", "status"
            ),
            subscription_transport_method=json_get_path(
                json_data, "payload", "subscription", "transport", "method"
            ),
            subscription_transport_session_id=json_get_path(
                json_data, "payload", "subscription", "transport", "session_id"
            ),
        )
