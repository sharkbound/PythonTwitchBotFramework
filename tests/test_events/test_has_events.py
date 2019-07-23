from twitchbot import BaseBot, Mod, Event


def test_base_bot_events_are_set():
    for event in Event:
        assert event.name in BaseBot.__dict__, f'BaseBot must implement event {event}'


def test_mod_events_are_set():
    for event in Event:
        assert event.name in Mod.__dict__, f'Mod must implement event {event}'
