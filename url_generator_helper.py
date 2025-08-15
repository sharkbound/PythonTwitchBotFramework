import json
from util import token_utils
from util.token_utils import Scopes

with open('configs/config.json', 'r') as f:
    secrets = json.load(f)

pubsub_url = token_utils.generate_auth_url(
    secrets["client_id"],
    'https://twitchapps.com/tmi/',
    'moderator:read:blocked_terms', 'moderator:read:chat_settings', 'moderator:read:unban_requests',
    'moderator:read:banned_users', 'moderator:read:chat_messages', 'moderator:read:warnings', 'moderator:read:vips',
    'moderator:read:moderators',
)
print(f'OAUTH URL: {token_utils.generate_irc_oauth(secrets["client_id"], "https://twitchapps.com/tmi/")}')
print(f'EVENTSUB: {pubsub_url}')
