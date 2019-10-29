from asyncio import sleep, get_event_loop

PRIVMSG_MAX_MOD = 100
PRIVMSG_MAX_NORMAL = 20

WHISPER_MAX = 10

privmsg_sent = 0
whisper_sent = 0


async def privmsg_ratelimit(channel):
    global privmsg_sent
    limit = PRIVMSG_MAX_NORMAL
    
    if channel.is_mod or channel.is_vip:
        limit = PRIVMSG_MAX_MOD

    while privmsg_sent >= limit:
        await sleep(1)

    privmsg_sent += 1


async def whisper_ratelimit():
    global whisper_sent

    while whisper_sent >= WHISPER_MAX:
        await sleep(1)

    whisper_sent += 1


async def privmsg_sent_reset_loop():
    global privmsg_sent

    while True:
        privmsg_sent = 0
        await sleep(30)


async def whisper_sent_reset_loop():
    global whisper_sent

    while True:
        whisper_sent = 0
        await sleep(1)


get_event_loop().create_task(privmsg_sent_reset_loop())
get_event_loop().create_task(whisper_sent_reset_loop())
