#!/usr/bin/env python3
import asyncio

import click
from urwid import AsyncioEventLoop, Edit, Filler, Frame, MainLoop, Text, connect_signal

loop = asyncio.get_event_loop()


@click.command()
@click.option('--host', prompt='Command server host', default='localhost')
@click.option('--port', prompt='Command server port', default='1337')
def run(host, port):
    lines = ['example text\n']
    output = Text(lines)
    input_field = Edit('>> ')
    widget = Frame(Filler(output, 'top'), footer=input_field)
    widget.focus_position = 'footer'
    event_loop=AsyncioEventLoop(loop=loop)
    def accept_input(key):
        if key == 'enter':
            lines.append(input_field.edit_text + '\n')
            input_field.set_edit_text('')
            output.set_text(lines)
    MainLoop(widget, event_loop=event_loop, unhandled_input=accept_input).run()

if __name__ == '__main__':
    run()
