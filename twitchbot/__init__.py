from .arena import *
from .channel import *
from .chatters import *
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
from .overrides import *
from .loyalty_ticker import *
from .disabled_commands import *
from .songrequest import *
from .web import *

load_commands_from_directory(os.path.join(__path__[0], 'builtin_commands'))
start_socket_server()
