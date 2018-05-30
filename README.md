# PythonTwitchBotFramework
working twitchbot framework made in python 3.6+

# basic info
This is a fully async twitch bot framework complete with:

* builtin command system using decorators
* overridable events (message received, whisper received, ect)
* full permission system that is individual for each channel
* message timers 
* quotes 
* custom commands
* builtin economy 


# quick start

the minimum code to get the bot running is this:
```python
from twitchbot.bots import BaseBot

if __name__ == '__main__':
    BaseBot().run()

```

this will start the bot. 

if you have a folder with your own custom commands you can load
the .py files in it with:
```python
from twitchbot import BaseBot, load_commands_from_directory

if __name__ == '__main__':
    load_commands_from_directory('PATH/TO/DIRECTORY')
    BaseBot().run()

```

* overriding events

the bots events are overridable via the following 2 ways:

1) using decorators:

```python
from twitchbot import override_event, Event, Message

@override_event(Event.on_privmsg_received)
async def on_privmsg_received(msg: Message):
    print(f'{msg.author} sent message {msg.content} to channel {msg.channel_name}')

```

2) subclassing BaseBot
```python
from twitchbot import BaseBot, Message
class MyCustomTwitchBot(BaseBot):
    @staticmethod
    async def on_privmsg_received(msg: Message):
        print(f'{msg.author} sent message {msg.content} to channel {msg.channel_name}')


```
then you would use MyCustomTwitchBot instead of BaseBot:
```python
MyCustomTwitchBot().run()
```

* all overridable events are:
```python
from twitchbot import Event

Event.on_after_command_execute : (msg: Message, cmd: Command)
Event.on_before_command_execute : (msg: Message, cmd: Command)
Event.on_bits_donated : (msg: Message, bits: int)
Event.on_channel_joined : (channel: Channel)
Event.on_connected : ()
Event.on_privmsg_received : (msg: Message)
Event.on_privmsg_sent : (msg: str, channel: str, sender: str)
Event.on_whisper_received : (msg: Message)
Event.on_privmsg_sent : (msg: str, receiver: str, sender: str)
```


if this is the first time running the bot it will generate a folder
named `configs`. 

inside is `config.json` which you put the authentication into

as the bot is used it will also generate channel permission files 
in the `configs` folder

# adding your own commands

to register your own commands use the Command decorator:

* using decorators
```python
from twitchbot import Command

@Command('COMMAND_NAME')
async def cmd_function(msg, *args):
    await msg.reply('i was called!')
```
* you can also limit the commands to be whisper or channel chat only 
(default is channel chat only)
```python
from twitchbot import Command, CommandContext

# other options are CommandContext.BOTH and CommandContext.WHISPER
@Command('COMMAND_NAME', context=CommandContext.CHANNEL) # this is the default command context
async def cmd_function(msg, *args):
    await msg.reply('i was called!')
```
* you can also specify if a permission is required to be able to call
the command (if no permission is specified anyone can call the command):

```python
from twitchbot import Command

@Command('COMMAND_NAME', permission='PERMISSION_NAME')
async def cmd_function(msg, *args):
    await msg.reply('i was called!')
```

* you can also specify a help/syntax for the command for the help chat command to give into on it:
```python
from twitchbot import Command, Message

@Command('COMMAND_NAME', help='this command does a very important thing!', syntax='<name>')
async def cmd_function(msg: Message, *args):
    await msg.reply('i was called!')
```
so when you do `!help COMMAND_NAME`

it will this in chat:
```
help for "!command_name", 
syntax: "<name>", 
help: "this command does a very important thing!"
```

# config

the default config values are:
```json
{
  "oauth": "oauth:",
  "client_id": "CLIENT_ID",
  "nick": "nick",
  "prefix": "!",
  "default_balance": 200,
  "owner": "BOT_OWNER_NAME",
  "channels": [
    "channel"
  ]
}

```

`oauth` is the twitch oauth used to login  

`client_id` is the client_id used to get info like channel title, ect ( this is not required but twitch API info will not be available without it )

`nick` is the twitch accounts nickname

`prefix` is the command prefix the bot will use for commands that 
dont use custom prefixes

`default_balance `is the default balance for new users that dont
already have a economy balance

`owner` is the bot's owner

`channels` in the twitch channels the bot will join

# permissions

the bot comes default with permission support

there are two ways to manage permissions,

1. using chat commands 
2. editing JSON permission files

## managing permissions using chat commands
to add a permission group: `!addgroup <group>`, ex: `!addgroup donators`

to add a member to a group: `!addmember <group> <user>`, ex: 
`!addmember donators johndoe`

to add a permission to a group: `!addperm <group> <permission>`, ex: 
`!addperm donators slap`

to remove a group: `!delgroup <group>`, ex: `!delgroup donators`

to remove a member from a group: `!delmember <group> <member>`, ex: 
`!delmember donators johndoe`

to remove a permission from a group: `!delperm <group> <permission>`, ex:
`!delperm donators slap`

## managing permission by editing the configs

find the `configs` folder the bot generated (will be in same directory as the 
script that run the bot)

inside you will find `config.json` with the bot config values required for 
authentication with twitch and such

if the bot has joined any channels then you will see file names
that look like `CHANNELNAME_perms.json`

for this example i will use a `johndoe`

so if you open `johndoe_perms.json` you will see this if you 
have not changed anything in it:

```json
{
  "admin": {
    "name": "admin",
    "permissions": [
      "*"
    ],
    "members": [
      "johndoe"
    ]
  }
}
```

`name` is the name of the permission group

`permissions` is the list of permissions the group has
("*" is the "god" permission, granting access to all bot commands)

`members` is the members of the group

to add more permission groups by editing the config 
you can just copy/paste the default one 
(be sure to remove the "god" permission if you dont them 
having access to all bot commands)

so after copy/pasting the default group it will look like this
 (dont forget to separate the groups using `,`):
 
 
```json
{
  "admin": {
    "name": "admin",
    "permissions": [
      "*"
    ],
    "members": [
      "johndoe"
    ]
  },
  "donator": {
    "name": "donator",
    "permissions": [
      "slap"
    ],
    "members": [
      "johndoe"
    ]
  }
}
```

if the bot is running be sure to do `!reloadperms` to load
the changes to the permission file