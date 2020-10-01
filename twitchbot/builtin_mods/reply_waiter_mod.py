from twitchbot import Mod, Message, reply_wait_queue, MessageType


class ReplyWaiter(Mod):
    name = 'replywaiter'
    TASK_NAME = ''

    async def on_raw_message(self, msg: Message):
        if not reply_wait_queue or msg.type not in {MessageType.WHISPER, MessageType.PRIVMSG}:
            return

        remove = []
        for i, (future, predicate) in enumerate(reply_wait_queue):
            if await predicate(msg):
                # set the result of the future to the message, this makes the future complete and return its result
                # FIXME: https://github.com/sharkbound/PythonTwitchBotFramework/issues/27
                # bug cause comes from trying to set result on cancelled futures
                if not future.cancelled():
                    future.set_result(msg)
                # need to move this to a thread/async save removal method
                remove.append(i)

        for i in reversed(remove):
            del reply_wait_queue[i]
