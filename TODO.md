# TODO

* add `add_repeating_task(name, coroutine, interval)`
  function that adds a coroutine to be called every [interval] seconds

# DONE

* `get_database_session()` function that validates and returns a connection
    * somewhat done, just returns the normal session for now, trying sqlalchemy timeout flags for now