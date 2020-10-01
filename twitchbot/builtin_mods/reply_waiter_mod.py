from twitchbot import Mod, Message, reply_wait_queue, MessageType, add_task, stop_task, task_running
import asyncio


class ReplyWaiter(Mod):
    name = 'replywaiter'
    TASK_NAME = '_reply_waiter_queue_removing_loop'

    async def loaded(self):
        if not task_running(self.TASK_NAME):
            add_task(self.TASK_NAME, self._reply_waiter_queue_removing_loop())

    async def unloaded(self):
        stop_task(self.TASK_NAME)

    def _is_future_writable(self, future):
        return not future.cancelled() and not future.done()

    async def _reply_waiter_queue_removing_loop(self):
        while True:
            if reply_wait_queue:
                # use range to allow for deletion from the queue, reverse the range order to avoid index shifts upon deletion
                for i in range(len(reply_wait_queue) - 1, -1, -1):
                    # future is in the index 0 of the tuples in the reply wait queue, 1 is the predicate
                    if not self._is_future_writable(reply_wait_queue[i][0]):
                        del reply_wait_queue[i]

            await asyncio.sleep(.1)

    async def on_raw_message(self, msg: Message):
        if not reply_wait_queue or msg.type not in {MessageType.WHISPER, MessageType.PRIVMSG}:
            return

        for i, (future, predicate) in enumerate(reply_wait_queue):
            if self._is_future_writable(future) and await predicate(msg):
                future.set_result(msg)
