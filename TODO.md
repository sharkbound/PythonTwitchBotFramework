# TODO

* add `add_repeating_task(name, coroutine, interval)`
  function that adds a coroutine to be called every [interval] seconds
* add option to pass channels, oauth, username, client_id directly to BaseBot to bypass config
* change IRC to not reference global state (like channels) to allow for the above change
* class commands (like mods, except has a execute(...) method), has name and such as class variables
* (half done) add option to allow for using twitch's reply system for comments in msg.reply(...) method

# DONE

* `get_database_session()` function that validates and returns a connection
    * somewhat done, just returns the normal session for now, trying sqlalchemy timeout flags for now