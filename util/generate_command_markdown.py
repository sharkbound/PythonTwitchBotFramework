from pathlib import Path
from twitchbot import commands, BaseBot
from shutil import rmtree
from os import remove

BaseBot()._load_builtin_commands()

with open('commands.md', 'w') as out:
    out.write('# Builtin Commands: \n')
    out.write('## index\n')

    for command in commands.values():
        out.write(f'\n* [{command.name}](#{command.name})')

    for command in commands.values():
        out.write(f"""

## {command.name}
NAME: {command.name}

SYNTAX: {command.syntax or 'NO SYNTAX'}

PERMISSION: {command.permission or 'NO PERMISSION'}

HELP: {command.help or 'NO HELP'}

[[back to index](#index)]
""")

# the bot creates these folders, and since we do not need them, just delete them
CWD = Path.cwd()
# noinspection PyTypeChecker

if (sqlite_file := (CWD / 'database.sqlite')).exists():
    remove(sqlite_file)
if (configs_directory := (CWD / 'configs')).exists():
    rmtree(configs_directory)
if (mods_directory := (CWD / 'mods')).exists():
    rmtree(mods_directory)
