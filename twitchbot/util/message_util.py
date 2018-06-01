import shlex


def split_message(msg: str):
    try:
        return shlex.split(msg)
    except ValueError:
        return msg.split(' ')
