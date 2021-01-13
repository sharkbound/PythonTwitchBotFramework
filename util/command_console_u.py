#!/usr/bin/env python3
import asyncio

import click
from urwid import AsyncioEventLoop, Edit, Filler, Frame, MainLoop, Text

loop = asyncio.get_event_loop()

@click.command()
@click.option('--host', prompt='Command server host', default='localhost')
@click.option('--port', prompt='Command server port', default='1337')
def run(host, port):
    lines = ['example text']
    output = Text(lines)
    input = Edit('>> ')
    widget = Frame(Filler(output, 'top'), footer=input)
    widget.focus_position = 'footer'
    event_loop=AsyncioEventLoop(loop=loop)
    MainLoop(widget, event_loop=event_loop).run()

if __name__ == '__main__':
    run()
