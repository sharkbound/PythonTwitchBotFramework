import webbrowser
from collections import namedtuple

__all__ = ('show_auth_gui', 'AuthInfo')

OAUTH_GENERATOR_URL = 'https://twitchapps.com/tmi/'
AuthInfo = namedtuple('AuthInfo', 'username oauth')


def show_auth_gui():
    try:
        import tkinter as tk
    except ImportError:
        print('unable to import tkinter to show the GUI!')
        return

    root = tk.Tk()
    width = 30

    tk.Label(root, text='bot account name:').grid(row=0, column=0)
    username = tk.StringVar(root)
    tk.Entry(root, textvar=username, width=width).grid(row=0, column=1)

    tk.Label(root, text='oauth:').grid(row=1, column=0)
    password = tk.StringVar(root)
    tk.Entry(root, show='*', textvar=password, width=width).grid(row=1, column=1)

    tk.Button(
        text='open twitch oauth generator website',
        command=lambda: webbrowser.open(OAUTH_GENERATOR_URL)
    ).grid(row=2, column=0)

    tk.Button(root, text='im done', command=lambda: root.destroy()).grid(row=2, column=1)

    root.mainloop()
    return AuthInfo(username=username.get(), oauth=password.get())
