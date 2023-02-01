from .bot_package_path import _set_bot_package_path, get_bot_package_path

BOT_VERSION = (2, 8, 0)
_set_bot_package_path(__path__[0])

from .arena import *
from .channel import *
from .api.chatters import *
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
from .disabled_commands import *
from .duel import *
from .command_server import start_command_server, CommandServerMessage, stop_command_server
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
from .translations import *
from .argument_annotations import *
from .auto_cast_handler import *