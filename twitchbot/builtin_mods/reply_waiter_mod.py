from twitchbot import Mod, Message, reply_wait_queue, MessageType


class ReplyWaiter(Mod):
    name = 'replywaiter'

    async def on_raw_message(self, msg: Message):
        if not reply_wait_queue or msg.type not in {MessageType.WHISPER, MessageType.PRIVMSG}:
            return

        remove = []
        for i, (future, predicate) in enumerate(reply_wait_queue):
            if await predicate(msg):
                # set the result of the future to the message, this makes the future complete and return its result
                future.set_result(msg)
                remove.append(i)

        for i in reversed(remove):
            del reply_wait_queue[i]
