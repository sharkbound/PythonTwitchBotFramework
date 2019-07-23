from twitchbot import BaseBot, Mod, Event, cfg


def test_base_bot_events_are_set():
    for event in Event:
        assert event.name in BaseBot.__dict__


def test_mod_events_are_set():
    for event in Event:
        assert event.name in Mod.__dict__
