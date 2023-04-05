import asyncio
import sys
import time
import typing
import enum
from typing import NamedTuple, Optional, Tuple, Dict, Any, List, Union

from aiohttp import ClientResponse

from .data import RateLimit
from .util import post_url, get_url, add_task, delete_url

__all__ = [
    'TwitchApiRatelimitQueue',
    'TwitchApiQueueSendHandler',
    'PendingTwitchAPIRequestMode',
    'start_twitch_api_queue_send_handler_loop',
    'twitch_api_queue_send_handler',
    'RATELIMITED_TWITCH_API_QUEUE_SEND_HANDLER_LOOP_TASK_NAME',
    'enqueue_twitch_api_request',
]

if typing.TYPE_CHECKING:
    from twitchbot import RateLimit
    
if sys.version_info >= (3, 10):
    ApiResponseFuture = asyncio.Future[Tuple[Optional[ClientResponse], Optional[Dict[str, Any]]]]
else:
    ApiResponseFuture = asyncio.Future

class PendingTwitchAPIRequestMode(enum.Enum):
    POST = enum.auto()
    GET = enum.auto()
    DELETE = enum.auto()


class _PendingTwitchApiRequest(NamedTuple):
    url: str
    headers: dict
    mode: PendingTwitchAPIRequestMode
    future: asyncio.Future
    body: Optional[Any] = None


class TwitchApiRatelimitQueue:
    def __init__(self):
        self.queue: asyncio.Queue[_PendingTwitchApiRequest] = asyncio.Queue()
        self.requests_left = 0
        self.limit = -1
        self.ratelimit_reset = -1

    async def wait_till_not_ratelimited(self):
        while self.is_currently_ratelimited:
            await asyncio.sleep(0.3)

    def update_ratelimit_reset(self, ratelimit: 'RateLimit'):
        self.ratelimit_reset = ratelimit.reset
        self.requests_left = ratelimit.remaining
        self.limit = ratelimit.limit

    @property
    def is_currently_ratelimited(self):
        # not currently ratelimited if the reset time is in the past, or no reset is epoch time is set
        if self.ratelimit_reset < time.time() or self.ratelimit_reset == -1:
            return False

        if self.requests_left <= 0:
            return True

        return False

    def append_url_request(
            self,
            url: str,
            headers: dict,
            mode: PendingTwitchAPIRequestMode,
            body: Optional[Any] = None
    ) -> ApiResponseFuture:
        fut = asyncio.Future()
        self.queue.put_nowait(_PendingTwitchApiRequest(url=url, headers=headers, future=fut, mode=mode, body=body))
        return fut

    async def next_request(self) -> Optional[_PendingTwitchApiRequest]:
        if self.queue.empty():
            return None
        return await self.queue.get()

    def __bool__(self):
        return not self.queue.empty()


class TwitchApiQueueSendHandler:
    def __init__(self):
        self.queue = TwitchApiRatelimitQueue()

    @property
    def has_next_request(self):
        return bool(self.queue)

    async def wait_till_not_ratelimited(self):
        return await self.queue.wait_till_not_ratelimited()

    @property
    def is_currently_ratelimited(self):
        return self.queue.is_currently_ratelimited

    def enqueue_url_request(
            self,
            url: str,
            headers: dict,
            mode: PendingTwitchAPIRequestMode,
            body: Optional[Any] = None
    ) -> ApiResponseFuture:
        return self.queue.append_url_request(url=url, headers=headers, mode=mode, body=body)

    async def handle_next_request(self):
        if not self.has_next_request or self.queue.is_currently_ratelimited:
            return

        ratelimit = None
        resp = None
        json = None

        request = await self.queue.next_request()
        if request.mode is PendingTwitchAPIRequestMode.POST:
            resp, json = await post_url(request.url, headers=request.headers, body=request.body)

        elif request.mode is PendingTwitchAPIRequestMode.GET:
            resp, json = await get_url(request.url, headers=request.headers)
        
        elif request.mode is PendingTwitchAPIRequestMode.DELETE:
            resp, json = await delete_url(request.url, headers=request.headers)

        if resp is not None and json is not None:
            request.future.set_result((resp, json))
        else:
            request.future.set_result((None, None))

        if resp is not None:
            ratelimit = RateLimit.from_headers_or_none(resp.headers)

        if ratelimit is not None:
            self.queue.update_ratelimit_reset(ratelimit)


twitch_api_queue_send_handler = TwitchApiQueueSendHandler()


async def _request_process_loop():
    while True:
        try:
            await twitch_api_queue_send_handler.handle_next_request()

        except asyncio.CancelledError:
            pass

        except Exception as _:
            import traceback
            traceback.print_exc()

        await asyncio.sleep(0.1)


RATELIMITED_TWITCH_API_QUEUE_SEND_HANDLER_LOOP_TASK_NAME = 'ratelimited_twitch_api_queue_send_handler_loop'


def start_twitch_api_queue_send_handler_loop():
    add_task(RATELIMITED_TWITCH_API_QUEUE_SEND_HANDLER_LOOP_TASK_NAME, asyncio.get_event_loop().create_task(_request_process_loop()))


def enqueue_twitch_api_request(url: str, headers: dict, mode: PendingTwitchAPIRequestMode, body: Optional[Any] = None) \
        -> ApiResponseFuture:
    return twitch_api_queue_send_handler.enqueue_url_request(url, headers, mode, body=body)
