from twitchbot import commands
from shutil import rmtree
from pathlib import Path
from os import remove

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
remove(CWD / 'database.sqlite')
rmtree(CWD / 'configs')
rmtree(CWD / 'mods')
