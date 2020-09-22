from .arena import *
from .channel import *
from twitchbot.api.chatters import *
from .colors import *
from .command import *
from .config import *
from .enums import *
from .irc import *
from .message import *
from .permission import *
from .ratelimit import *
from .regex import *
from .util import *
from .database import *
from .bots import *
from .api import *
from .events import *
from .loyalty_ticker import *
from .disabled_commands import *
from .duel import *
from .command_server import start_command_server
from .modloader import *
from .disabled_mods import *
from .data import *
from .exceptions import *
from .shared import *
from .replywaiter import *
from .command_whitelist import *
from .poll import *
from .event_util import *
from .extra_configs import *
from .pubsub import *
from . import builtin_commands
from . import builtin_mods

BOT_VERSION = (1, 16, 3)  # keep in sync with version in setup.py:11

import os

load_commands_from_directory(os.path.join(__path__[0], 'builtin_commands'))

load_mods_from_directory(os.path.join(__path__[0], 'builtin_mods'))
load_mods_from_directory(os.path.abspath(cfg.mods_folder))

ensure_mods_folder_exists()
ensure_commands_folder_exists()

load_commands_from_directory(os.path.abspath(cfg.commands_folder))
start_command_server()
