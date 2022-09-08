import asyncio
import inspect
from asyncio import Future, TimeoutError
from typing import List, Callable, Tuple, Awaitable, Union, Any

from .message import Message

__all__ = [
    'reply_wait_queue',
    'ReplyWaitType',
    'same_author_and_channel_predicate',
    'same_channel_predicate',
    'wait_for_reply',
    'custom_predicate',
    'custom_async_predicate',
    'ReplyResult',
]

ReplyWaitType = Tuple[Future, Callable[..., Awaitable[bool]]]

# list of futures and coroutines that are waiting for a message reply
# first item in each tuple must be a Future, this is because it is later given a value if the Awaitable return True
# second item in each tuple must be a Awaitable that return True or False
# a True return from the Awaitable means the message was accepted, and the Future has its result set to the message
reply_wait_queue: List[ReplyWaitType] = []


def same_author_and_channel_predicate(msg: Message):
    """
    returns a async predicate where the message from be from the same author and channel as `msg` passed to this function
    """

    async def _same_author_predicate(m):
        return m.channel == msg.channel and m.author == msg.author and m.content != msg.content

    return _same_author_predicate


def same_channel_predicate(msg: Message):
    """
    returns a async predicate where the message from be from the same channel as `msg` passed to this function
    """

    async def _same_channel_predicate(m):
        return m.channel == msg.channel

    return _same_channel_predicate


def custom_predicate(custom_predicate: Callable[[Message], bool] = None,
                     same_author=True,
                     same_channel=True,
                     msg: Message = None):
    """
    returns a async predicate where the custom_predicate must return True when called with the message

    if same_author is True, then the message must come from the same author who sent msg

    if same_channel is True, then the message must come from the same channel as msg was sent from
    """

    if not msg and any((same_author, same_channel)):
        raise ValueError(
            'msg cannot be None if same_author or same_channel is True, add `msg=MSG_HERE` to fix this error')

    async def _custom_predicate(m: Message):
        if (same_channel and m.channel != msg.channel) or (same_author and m.author != msg.author):
            return False

        if custom_predicate is not None:
            return custom_predicate(m)

        return True

    return _custom_predicate


def custom_async_predicate(msg: Message, custom_predicate: Callable[[Message], Awaitable[bool]] = None,
                           same_author=True,
                           same_channel=True):
    async def _custom_async_predicate(m: Message):
        if (same_channel and m.channel != msg.channel) or (same_author and m.author != msg.author):
            return False

        if custom_predicate is not None:
            return await custom_predicate(m)

        return True

    return _custom_async_predicate


class ReplyResult:
    def __init__(self, data, default=None, timed_out=False):
        self.timed_out = timed_out
        self.default_value = default
        self.raw_value = data
        self.has_value = data is not None

    @property
    def is_message(self) -> bool:
        return isinstance(self.raw_value, Message)

    @property
    def is_default(self):
        return self.raw_value == self.default_value

    @property
    def content(self) -> str:
        if isinstance(self.raw_value, Message):
            return self.raw_value.content
        return str(self.raw_value)

    def __str__(self):
        return str(self.raw_value)


TYPE_CALLABLE_PREDICATE = Union[Callable[['Message'], Awaitable[bool]], Callable[['Message'], bool]]


async def wait_for_reply(predicate: TYPE_CALLABLE_PREDICATE = None, timeout=30, default=None, raise_on_timeout=False) -> ReplyResult:
    """
    waits for a message matching `predicate` to be received, when its received, it returns a ReplyResult instance with the response.

    if no message matching `predicate` is received by the timeout, a ReplyResult instance will be returned with the default as its value.

    if raise_on_timeout is True and no matching message is received, this function will raise asyncio.TimeoutError

    if raise_on_timeout is False and no matching message is received, a ReplyResult with default as its value will be returned when it times-out

    default is None by default

    raise_on_timeout is False by default
    """

    async def _timeout_defaulter():
        timed_out = False
        try:
            value = await asyncio.wait_for(future, timeout)
        except TimeoutError:
            timed_out = True
            if raise_on_timeout:
                raise
            else:
                value = default

        return ReplyResult(value, default=default, timed_out=timed_out)

    # ensures that the predicate is a coroutine (aka awaitable)
    if not inspect.iscoroutinefunction(predicate):
        # predicate=predicate is needed because python closure variable are late binding
        async def _async_predicate_wrapper(msg, predicate=predicate):
            return predicate(msg)

        predicate = _async_predicate_wrapper

    future = asyncio.get_event_loop().create_future()
    reply_wait_queue.append((future, predicate))
    return await _timeout_defaulter()
