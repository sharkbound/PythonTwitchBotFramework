# PythonTwitchBotFramework
working twitchbot framework made in python 3.6+

#basic info
This is a fully async twitch bot framework complete with:

* builtin command system using decorators
* overridable events (message received, whisper received, ect)
* full permission system that is individual for each channel
* message timers 
* quotes 
* custom commands 


# quick start

the minimum code to get the bot running is this:
```python
import asyncio
from twitchbot.bots import BaseBot

async def main():
    bot = await BaseBot.create()
    await bot.start()

asyncio.get_event_loop().run_until_complete(main())

```

this will start the bot. 

if this is the first time running the bot it will generate a folder
named `configs`. 

inside is `config.json` which you put the authentication into

as the bot is used it will also generate channel permission files 
in the `configs` folder

# adding your own commands

to register your own command you have 2 options:
to register your own command you have 2 options: