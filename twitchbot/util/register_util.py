__all__ = ['auto_register_mod']


def auto_register_mod(obj):
    """
    registers the mod when the files is loaded

    example:
    >>> from twitchbot import Message
    >>>
    >>> @auto_register_mod
    >>> class MyMod(Mod):
    >>>     async def on_privmsg_received(self, msg: Message):
    >>>         print(f'MyMod got the message: {msg.content}')

    :param obj:
    :return:
    """
    # getting around circular import issues
    from ..modloader import Mod, register_mod

    if issubclass(obj, Mod):
        register_mod(obj())
    elif isinstance(obj, Mod):
        register_mod(obj)
    else:
        raise ValueError(f'Unsupported auto_register class: {obj} type: {type(obj)}')

    return obj
