import json
from util import token_utils
from util.token_utils import Scopes

with open('configs/config.json', 'r') as f:
    secrets = json.load(f)

pubsub_url = token_utils.generate_auth_url(
    secrets["client_id"],
    'https://twitchapps.com/tmi/',
    Scopes.PUBSUB_CHANNEL_POINTS,
    Scopes.PUBSUB_BITS,
    Scopes.PUBSUB_CHANNEL_SUBSCRIPTION,
)
print(f'OAUTH URL: {token_utils.generate_irc_oauth(secrets["client_id"], "https://twitchapps.com/tmi/")}')
print(f'PUBSUB: {pubsub_url}')
