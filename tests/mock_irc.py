from twitchbot import Irc


class MockIrc(Irc):
    def __init__(self):
        super().__init__(None, None)
