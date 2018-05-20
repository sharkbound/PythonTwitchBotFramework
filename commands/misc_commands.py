import re
from typing import Dict

from arena import Arena, ARENA_DEFAULT_ENTRY_FEE
from channel import channels
from command import Command, commands
from enums import CommandContext
from message import Message
from database import get_all_custom_commands, get_balance, get_currency_name, add_balance


@Command('list')
async def cmd_list(msg: Message, *args):
    for c in channels.values():
        await msg.reply(whisper=True,
                        msg=f'channel: {c.name}, viewers: {c.chatters.viewer_count}, is_mod: {c.is_mod}, is_live: {c.live}')


@Command('help', context=CommandContext.BOTH)
async def cmd_help(msg: Message, *args):
    custom_commands_str = ', '.join(cmd.name for cmd in get_all_custom_commands(msg.channel_name))
    global_commands_str = ', '.join(cmd.fullname for cmd in commands.values())

    await msg.reply(whisper=True, msg=f'GLOBAL: {global_commands_str}')

    if custom_commands_str:
        await msg.reply(whisper=True, msg=f'CUSTOM: {custom_commands_str}')


Command(name='commands')(cmd_help.func)

running_arenas: Dict[str, Arena] = {}


@Command('arena')
async def cmd_arena(msg: Message, *args):
    def _can_pay_entry_fee(fee):
        return get_balance(msg.channel_name, msg.author).balance >= fee

    arena = running_arenas.get(msg.channel_name)
    curname = get_currency_name(msg.channel_name).name

    # arena is already running for this channel
    if arena:
        if msg.author in arena.users:
            await msg.reply(
                whisper=True,
                msg='you are already entered the in the arena')
            return

        elif not _can_pay_entry_fee(arena.entry_fee):
            await msg.reply(
                whisper=True,
                msg=f'{msg.mention} you do not have enough {curname} '
                    f'to join the arena, entry_fee is {arena.entry_fee} {curname}')
            return

        arena.add_user(msg.author)
        add_balance(msg.channel_name, msg.author, -arena.entry_fee)

        await msg.reply(
            whisper=True,
            msg=f'{msg.mention} you have been added to the arena, you were charged {arena.entry_fee} {curname} upon entry')

    # start a new arena as one is not already running for this channel
    else:
        if args:
            try:
                entry_fee = int(args[0])
            except ValueError:
                await msg.reply(msg='invalid value for entry fee')
                return
        else:
            entry_fee = ARENA_DEFAULT_ENTRY_FEE

        if entry_fee and entry_fee < ARENA_DEFAULT_ENTRY_FEE:
            await msg.reply(msg=f'entry fee cannot be less than {ARENA_DEFAULT_ENTRY_FEE}')
            return

        if not _can_pay_entry_fee(entry_fee):
            await msg.reply(
                whisper=True,
                msg=f'{msg.mention} you do not have {entry_fee} {curname}')
            return

        arena = Arena(msg.channel, entry_fee, on_arena_ended_func=_remove_running_arena_entry)
        arena.start()
        arena.add_user(msg.author)

        add_balance(msg.channel_name, msg.author, -arena.entry_fee)

        running_arenas[msg.channel_name] = arena
        print('STARTED ARENA')


def _remove_running_arena_entry(arena: Arena):
    global running_arenas

    try:
        del running_arenas[arena.channel.name]
        print('success')
    except:
        pass
