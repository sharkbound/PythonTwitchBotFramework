# if you have any questions concerning the bot, you can contact me in my discord server: https://discord.gg/PXrKVHp OR [r/pythontwitchbot](https://www.reddit.com/r/pythontwitchbot/) on reddit

if you would like to send a few dollars my way you can do so
here: [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=9ZVUE7CR24738)

this bot is also on PYPI: https://pypi.org/project/PythonTwitchBotFramework/

install from pip: `pip install PythonTwitchBotFramework`

# PythonTwitchBotFramework

fully async twitchbot framework/library compatible with python 3.6+

First and foremost, I want to thank anyone who uses this, or even is just reading this readme,
and to any contributors who have helped with updates/features.

## Note about the wiki and readme right now:

I am in the process of adding missing info to the wiki/readme,
and also updating to show the new command argument handling added in 2.7.0+.
(referring to the fact the command system now supporting and enforcing typehints, and not requiring *args anymore)

As well as some features i didn't put in the wiki or readme yet.

If you are any version earlier than 2.7.0, some things showcased/described on the wiki may not work for you.

## How to stop the bot

to stop the bot running, do any of these commands:

`!shutdown` or `!stop` in the twitch chat of the channel its in, this command tries to properly shutdown all the
tasks the bot is currently running and gives time to stop/cancel

these commands require the caller have permission to execute them

# Note:

### This readme only goes over basic info meant to help quickly get something working, the [GITHUB WIKI](https://github.com/sharkbound/PythonTwitchBotFramework/wiki) goes more in depth.

# Index

* [Quick Start](#quick-start)
* [Overriding Events](#overriding-events)
* [Overriding Events On Mods](#overriding-events-on-mods)
* [Adding Commands](#adding-commands)
* [SubCommands](#subcommands)
* [DummyCommands](#dummycommands)
* [Permissions](#permissions)
    * [Using Chat Commands](#managing-permissions-using-chat-commands)
    * [Editing The Config](#managing-permission-by-editing-the-configs)
* [Reloading Permissions](#reloading-permissions)
* [Command Server](#command-server)
* [Command Console](#command-console)
* [Database Support](#database-support)
* [Command Whitelist](#command-whitelist)
* [Twitch PubSub Client](#twitch-pubsub-client)

# Basic info

This is a fully async twitch bot framework complete with:

* builtin command system using decorators
* overridable events (message received, whisper received, ect)
* full permission system that is individual for each channel
* message timers
* quotes
* custom commands
* builtin economy

there is also mod system builtin to the bot, there is a collection of pre-made mods
here: [MODS](https://github.com/sharkbound/twitch_bot_mods)

# Quick Start

for a reference for builtin command look at the
wiki [HERE](https://github.com/sharkbound/PythonTwitchBotFramework/wiki/Builtin_Command_Reference)

the minimum code to get the bot running is this:

```python
from twitchbot import BaseBot

if __name__ == '__main__':
    BaseBot().run()
```

this will start the bot.

if you have a folder with your own custom commands you can load the .py files in it with:

```python
from twitchbot import BaseBot

if __name__ == '__main__':
    BaseBot().run()
```

# Overriding Events

the bots events are overridable via the following 2 ways:

## Using decorators:

```python
from twitchbot import event_handler, Event, Message


@event_handler(Event.on_privmsg_received)
async def on_privmsg_received(msg: Message):
    print(f'{msg.author} sent message {msg.content} to channel {msg.channel_name}')
```

## Subclassing BaseBot

```python
from twitchbot import BaseBot, Message


class MyCustomTwitchBot(BaseBot):
    async def on_privmsg_received(self, msg: Message):
        print(f'{msg.author} sent message {msg.content} to channel {msg.channel_name}')
```

then you would use MyCustomTwitchBot instead of BaseBot:

```python
MyCustomTwitchBot().run()
```

## Overriding Events On Mods

Visit [***the mods wiki page***](https://github.com/sharkbound/PythonTwitchBotFramework/wiki/Mods#index)
on this repo's wiki to view how to do it via Mods

* all overridable events are:

#### when using the decorator event override way, `self` is not included, ex: `(self, msg: Message)` becomes: `(msg: Message)`

```python
from twitchbot import Event

Event.on_connected: (self)
Event.on_permission_check: (self, msg
                            : Message, cmd: Command) -> Optional[
    bool]  # return False to deny permission to execute the cmd, Return None to ignore and continue
Event.on_after_command_execute: (self, msg: Message, cmd: Command)
Event.on_before_command_execute: (self, msg: Message, cmd: Command) -> bool  # return False to cancel command
Event.on_bits_donated: (self, msg: Message, bits: int)
Event.on_channel_raided: (self, channel: Channel, raider: str, viewer_count: int)
Event.on_channel_joined: (self, channel: Channel)
Event.on_channel_subscription: (self, subscriber: str, channel: Channel, msg: Message)
Event.on_privmsg_received: (self, msg: Message)
Event.on_privmsg_sent: (self, msg: str, channel: str, sender: str)
Event.on_whisper_received: (self, msg: Message)
Event.on_whisper_sent: (self, msg: str, receiver: str, sender: str)
Event.on_raw_message: (self, msg: Message)
Event.on_user_join: (self, user: str, channel: Channel)
Event.on_user_part: (self, user: str, channel: Channel)
Event.on_mod_reloaded: (self, mod: Mod)
Event.on_channel_points_redemption: (self, msg: Message, reward: str)
Event.on_bot_timed_out_from_channel: (self, msg: Message, channel: Channel, seconds: int)
Event.on_bot_banned_from_channel: (self, msg: Message, channel: Channel)
Event.on_poll_started: (self, channel: Channel, poll: PollData)
Event.on_poll_ended: (self, channel: Channel, poll: PollData)
Event.on_pubsub_received: (self, raw: 'PubSubData')
Event.on_pubsub_custom_channel_point_reward: (self, raw: 'PubSubData', data: 'PubSubPointRedemption')
Event.on_pubsub_bits: (self, raw: 'PubSubData', data: 'PubSubBits')
Event.on_pubsub_moderation_action: (self, raw: 'PubSubData', data: 'PubSubModerationAction')
Event.on_pubsub_subscription: (self, raw: 'PubSubData', data: 'PubSubSubscription')
Event.on_pubsub_twitch_poll_update: (self, raw: 'PubSubData', poll: 'PubSubPollData')
Event.on_pubsub_user_follow: (self, raw: 'PubSubData', data: 'PubSubFollow')
Event.on_bot_shutdown: (self)
Event.on_after_database_init(self)  # used for triggering database operations after the bot starts
```

if this is the first time running the bot it will generate a folder named `configs`.

inside is `config.json` which you put the authentication into

as the bot is used it will also generate channel permission files in the `configs` folder

# Adding Commands

to register your own commands use the Command decorator:

* Using decorators

```python
from twitchbot import Command, Message


@Command('COMMAND_NAME')
async def cmd_function(msg: Message):
    await msg.reply('i was called!')
```

* you can also limit the commands to be whisper or channel chat only
  (default is channel chat only)

```python
from twitchbot import Command, CommandContext, Message


# other options are CommandContext.BOTH and CommandContext.WHISPER
@Command('COMMAND_NAME', context=CommandContext.CHANNEL)  # this is the default command context
async def cmd_function(msg: Message):
    await msg.reply('i was called!')
```

* you can also specify if a permission is required to be able to call the command (if no permission is specified anyone
  can call the command):

```python
from twitchbot import Command, Message


@Command('COMMAND_NAME', permission='PERMISSION_NAME')
async def cmd_function(msg: Message):
    await msg.reply('i was called!')
```

* you can also specify a help/syntax for the command for the help chat command to give into on it:

```python
from twitchbot import Command, Message


@Command('COMMAND_NAME', help='this command does a very important thing!', syntax='<name>')
async def cmd_function(msg: Message):
    await msg.reply('i was called!')
```

so when you do `!help COMMAND_NAME`

it will this in chat:

```
help for "!command_name", 
syntax: "<name>", 
help: "this command does a very important thing!"
```

* you can add aliases for a command (other command names that refer to the same command):

```python
from twitchbot import Command, Message


@Command('COMMAND_NAME',
         help='this command does a very important thing!',
         syntax='<name>',
         aliases=['COMMAND_NAME_2', 'COMMAND_NAME_3'])
async def cmd_function(msg: Message):
    await msg.reply('i was called!')
```

`COMMAND_NAME_2` and `COMMAND_NAME_2` both refer to `COMMAND_NAME` and all three execute the same command

# SubCommands

the SubCommand class makes it easier to implement different actions based on a parameters passed to a command.

its the same as normal command except thats its not a global command

example: `!say` could be its own command, then it could have the sub-commands `!say myname` or `!say motd`.

you can implements this using something like this:

```python
from twitchbot import Command, Message


@Command('say')
async def cmd_say(msg: Message, *args):
    # args is empty
    if not args:
        await msg.reply("you didn't give me any arguments :(")
        return

    arg = args[0].lower()
    if arg == 'myname':
        await msg.reply(f'hello {msg.mention}!')

    elif arg == 'motd':
        await msg.reply('the message of the day is: python is awesome')

    else:
        await msg.reply(' '.join(args))


```

that works, but it can be done in a nicer way using the `SubCommand` class:

```python
from twitchbot import Command, SubCommand, Message


@Command('say')
async def cmd_say(msg: Message, *args):
    await msg.reply(' '.join(args))


# we pass the parent command as the first parameter   
@SubCommand(cmd_say, 'myname')
async def cmd_say_myname(msg: Message):
    await msg.reply(f'hello {msg.mention}!')


@SubCommand(cmd_say, 'motd')
async def cmd_say_motd(msg: Message):
    await msg.reply('the message of the day is: python is awesome')
```

both ways do the same thing, what you proffer to use is up to you, but it does make it easier to manage for larger
commands to use SubCommand class

# DummyCommands

this class is basically a command that does nothing when executed, its mainly use is to be used as base command for
sub-command-only commands

it has all the same options as a regular Command

when a dummy command is executed it looks for sub-commands with a matching name as the first argument passed to it

if no command is found then it will say in chat the available sub-commands

but if a command is found it executes that command

say you want a command to greet someone, but you always want to pass the language, you can do this:

```python
from twitchbot import DummyCommand, SubCommand, Message

# cmd_greet does nothing itself when called
cmd_greet = DummyCommand('greet')


@SubCommand(cmd_greet, 'english')
async def cmd_greet_english(msg: Message):
    await msg.reply(f'hello {msg.mention}!')


@SubCommand(cmd_greet, 'spanish')
async def cmd_greet_spanish(msg: Message):
    await msg.reply(f'hola {msg.mention}!')
```

doing just `!greet` will make the bot say:

```text
command options: {english, spanish}
```

doing `!greet english` will make the bot say this:

```text
hello @johndoe!
```

doing `!greet spanish` will make the bot say this:

```text
hola @johndoe!
```

# Config

the default config values are:

```json
{
  "nick": "nick",
  "oauth": "oauth:",
  "client_id": "CLIENT_ID",
  "prefix": "!",
  "default_balance": 200,
  "loyalty_interval": 60,
  "loyalty_amount": 2,
  "owner": "BOT_OWNER_NAME",
  "channels": [
    "channel"
  ],
  "mods_folder": "mods",
  "commands_folder": "commands",
  "command_server_enabled": true,
  "command_server_port": 1337,
  "command_server_host": "localhost",
  "disable_whispers": false,
  "use_command_whitelist": false,
  "send_message_on_command_whitelist_deny": true,
  "command_whitelist": [
    "help",
    "commands",
    "reloadcmdwhitelist",
    "reloadmod",
    "reloadperms",
    "disablemod",
    "enablemod",
    "disablecmdglobal",
    "disablecmd",
    "enablecmdglobal",
    "enablecmd",
    "addcmd",
    "delcmd",
    "updatecmd",
    "cmd"
  ]
}
```

`oauth` is the twitch oauth used to login

`client_id` is the client_id used to get info like channel title, ect ( this is not required but twitch API info will
not be available without it )

`nick` is the twitch accounts nickname

`prefix` is the command prefix the bot will use for commands that dont use custom prefixes

`default_balance `is the default balance for new users that dont already have a economy balance

`owner` is the bot's owner

`channels` in the twitch channels the bot will join

`loyalty_interval` the interval for which the viewers will given currency for watching the stream, gives amount
specified by `loyalty_amount`

`loyalty_amount` the amount of currency to give viewers every `loyalty_interval`

`command_server_enabled` specifies if the command server should be enabled (see [Command Server](#command-server) for
more info)

`command_server_port` the port for the command server

`command_server_host` the host name (address) for the command server

`disable_whispers` is this value is set to `true` all whispers will be converted to regular channel messages

`use_command_whitelist` enabled or disables the command whitelist (see [Command Whitelist](#command-whitelist))

`send_message_on_command_whitelist_deny` should the bot tell users when you try to use a non-whitelisted command?

`command_whitelist` json array of commands whitelisted without their prefix (only applicable
if [Command Whitelist](#command-whitelist) is enabled)

# Permissions

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

### tip: revoking permission for a group (aka negating permissions)

to revoke a permission for a group, add the same permission but with a - in front of it

ex: you can to prevent group B from using permission `feed` from group A.

Simply add its negated version to group B: `-feed`, this PREVENTS group B from having the permission `feed` from group A

## managing permission by editing the configs

find the `configs` folder the bot generated (will be in same directory as the script that run the bot)

inside you will find `config.json` with the bot config values required for authentication with twitch and such

if the bot has joined any channels then you will see file names that look like `CHANNELNAME_perms.json`

for this example i will use a `johndoe`

so if you open `johndoe_perms.json` you will see this if you have not changed anything in it:

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

to add more permission groups by editing the config you can just copy/paste the default one
(be sure to remove the "god" permission if you dont them having access to all bot commands)

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

# Reloading Permissions

if the bot is running be sure to do `!reloadperms` to load the changes to the permission file

# Command Server

The command server is a small Socket Server the bot host that lets the Command Console be able to make the bot send
messages given to it through a console. (see [Command Console](#command-console))

The server can be enabled or disabled through the config (see [Config](#config)), the server's port and host are
specified by the config file

# Command Console

If the [Command Server](#command-server) is disabled in the [config](#config) the Command Console cannot be used

The Command Console is used to make the bot send chat messages and commands

To launch the Command Console make sure the bot is running, and the [Command Server](#command-server) is enabled in
the [Config](#config),

after verifying these are done, simply do `python command_console.py` to open the console, upon opening it you will be
prompted to select a twitch channel that the bot is currently connected to.

after choose the channel the prompt changes to `(CHANNEL_HERE):` and you are now able to send chat messages / commands
to the choosen channel by typing your message and pressing enter

# Database Support

to enabled database support

* open `configs/database_config.json` (if its missing run the bot and close it, this should
  generate `database_config.json`)
* set `enabled` to `true`
* fill in `address`, `port`, `username`, `password`, and `database` (you will need to edit `driver`/`database_format` if
  you use something other than mysql or sqlite)
* install the mysql library (if needed) FOR MYSQL INSTALL: `pip install --upgrade --user mysql-connector-python`, or any
  other database supported by sqlalchemy, see the
  sqlalchemy [engines](https://docs.sqlalchemy.org/en/13/core/engines.html). like for example POSTGRES:
  `pip install --upgrade psycopg2`
* rerun the bot

# Command Whitelist

Command whitelist is a optional feature that only allows certain commands to be used (specified in the config)

it is disabled by default, but can be enabled by setting `use_command_whitelist` to `true` in `configs/config.json`

Command Whitelist limits what commands are enabled / usable on the bot

if a command that is not whitelisted is ran, it will tell the command caller that it is not whitelisted
if `send_message_on_command_whitelist_deny` is set to `true`, otherwise it will silently NOT RUN the command

whitelisted commands can be edited with the `command_whitelist` json-array in `configs/config.json`

to edit the command whitelist, you can add or remove elements from the `command_whitelist` json-array, do not include
the command's prefix, AKA `!command` becomes `command` in `command_whitelist`

### To reload the whitelist, restart the bot, or do `!reloadcmdwhitelist` in your the twitch chat (requires having `manage_commands` permission)

# Twitch PubSub Client

## what is pubsub?

pubsub is the way twitch sends certain events to subscribers to the topic it originates from

all topics are listed under the `PubSubTopics`
enum [found here](https://github.com/sharkbound/PythonTwitchBotFramework/blob/master/twitchbot/pubsub/topics.py)

## Requirements

### Step 1: creating a developer application

to create a twitch developer application [generate one here](https://dev.twitch.tv/console/apps), this requires the
account have two-factor enabled

1. visit [https://dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps)
1. click `+ Register new application`
1. for redirect uri set it as `https://twitchapps.com/tmi/`, then click `add`
1. for the purpose of the application, select `Chat Bot`
1. for name, you can do anything, as long as it does not contain `twitch` in it
1. finally, create the application

## Step 2: generating a new irc oauth access token with the new client_id

this step is needed because twitch requires that oauth tokens used in API calls be generated the client_id sent in the
api request

after you create the application click it and copy its client id, then paste it into the bot's config.json file located
at `configs/config.json` for the field `client_id`, like so:

```json
{
  "client_id": "CLIENT_ID_HERE"
}
```

now you need to generate a oauth for the bot's primary irc oauth that matches the client_id, there is a utility i
made [HERE](https://github.com/sharkbound/PythonTwitchBotFramework/blob/master/util/token_utils.py) to help with token
authorization URL generation

using that utility, add this code to the bottom of the util script .py file, you would generate the URL like so:

```python
print(generate_irc_oauth('CLIENT_ID_HERE', 'REDIRECT_URI_HERE'))
```

OR just replace the values in this auth url:

```
https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=<CLIENT_ID>&redirect_uri=<REDIRECT_URI>&scope=chat:read+chat:edit+channel:moderate+whispers:read+whispers:edit+channel_editor
```

open a browser window that is logged into your bot account and visit the values-replaced authorization URL

after you authorize it, copy the oauth access token and paste it into the bot's config for the value of `oauth`, ex:

```json
{
  "oauth": "oauth:<OAUTH_HERE>"
}
```

this ensures that API calls still work.

## Step 3: creating the pubsub oauth access token

this oauth token is responsible for actually allowing the bot to access oauth topics on a specific channel

the list of scopes needed for different topics can be found [HERE](https://dev.twitch.tv/docs/pubsub#topics), each topic
has its own scope it needs, all the scope permissions as strings for my util script can be found here:
[https://github.com/sharkbound/PythonTwitchBotFramework/blob/master/util/token_utils.py#L4](https://github.com/sharkbound/PythonTwitchBotFramework/blob/master/util/token_utils.py#L4)

(if you dont want to use the util script just use this url and add the needed
info: `https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={client_id}&redirect_uri={redirect}&scope={scopes}`
, scopes are separated with a + in the url)

(the following will use my util script, this also assumes you have downloaded/copied the token utility script as well)

to create the pubsub token, first decide on WHAT topics it needs to listen to, i will use `PubSubTopics.channel_points`
with this example

using the utility script, you can call `generate_auth_url` to generate the authorization URL for you

```python
print(generate_auth_url('CLIENT_ID_HERE', 'REDIRECT_URI_HERE', Scopes.PUBSUB_CHANNEL_POINTS))
```

### Required OAuth Scopes for PubSub topics

```
|____________________________|______________________________|
|            TOPIC           |      REQUIRED OAUTH SCOPE    |
|____________________________|______________________________|
followers                     -> channel_editor
polls                         -> channel_editor
bits                          -> bits:read
bits badge notification       -> bits:read
channel points                -> channel:read:redemptions
community channel points      -> (not sure, seems to be included in the irc oauth)
channel subscriptions         -> channel_subscriptions
chat (aka moderation actions) -> channel:moderate
whispers                      -> whispers:read
channel subscriptions         -> channel_subscriptions
```

the `[PubSubTopics.channel_points]` is the list of scopes to add to the authorization request url

after the URL is printed, copy it and visit/send the url to owner of the channel that you want pubsub access to

in the case of it being your own channel its much more simple, since you just need to visit it on your main account and
copy the oauth access code

## Using the pubsub oauth

1. go to the bot's folder/directory on the computer running
1. look for the `mods` folder
1. create `pubsub_subscribe.py` in the `mods` directory
1. paste the following template in it:

```python
from twitchbot import PubSubTopics, Mod, get_pubsub


class PubSubSubscriberMod(Mod):
    async def on_connected(self):
        await get_pubsub().listen_to_channel('CHANNEL_HERE', [PubSubTopics.channel_points],
                                             access_token='PUBSUB_OAUTH_HERE')

    # only needed in most cases for verifying a connection
    # this can be removed once verified
    async def on_pubsub_received(self, raw: 'PubSubData'):
        # this should print any errors received from twitch
        print(raw.raw_data)
```

after a successful pubsub connection is established, you can override the appropriate event (some pubsub topics dont
have a event yet, so use on_pubsub_received for those)

following the above example we will override the `Event.on_pubsub_custom_channel_point_reward` event

```python
from twitchbot import PubSubTopics, Mod, get_pubsub


class PubSubSubscriberMod(Mod):
    async def on_connected(self):
        await get_pubsub().listen_to_channel('CHANNEL_HERE', [PubSubTopics.channel_points],
                                             access_token='PUBSUB_OAUTH_HERE')

    # only needed in most cases for verifying a connection
    # this can be removed once verified
    async def on_pubsub_received(self, raw: 'PubSubData'):
        # this should print any errors received from twitch
        print(raw.raw_data)

    # twitch only sends non-default channel point rewards over pubsub 
    async def on_pubsub_custom_channel_point_reward(self, raw: 'PubSubData', data: 'PubSubPointRedemption'):
        print(f'{data.user_display_name} has redeemed {data.reward_title}')
```

that pretty much summarized how to use pubsub, if you have any more questions, or need help, do visit my discord server
or subreddit (found at top of this readme)