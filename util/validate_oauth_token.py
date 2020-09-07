import requests

VALIDATE_URL = 'https://id.twitch.tv/oauth2/validate'


def validate_oauth(token: str) -> dict:
    return requests.get(VALIDATE_URL, headers={'Authorization': f'OAuth {token}'}).json()


print(validate_oauth('TOKEN_NO_PREFIX'))
