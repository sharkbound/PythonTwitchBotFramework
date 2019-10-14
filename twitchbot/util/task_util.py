from asyncio import ensure_future, Task, sleep, get_event_loop
from typing import Dict, Coroutine, Optional

__all__ = ('active_tasks', 'add_task', 'get_task', 'task_running', 'stop_task', 'task_exist', 'stop_all_tasks')

active_tasks: Dict[str, Task] = {}


def add_task(name: str, coro: Coroutine):
    active_tasks[name.lower()] = ensure_future(coro)


def get_task(name: str) -> Optional[Task]:
    return active_tasks.get(name.lower())


def task_exist(name: str):
    return name.lower() in active_tasks


def stop_all_tasks():
    for task in active_tasks.values():
        task.cancel()


def stop_task(name: str) -> bool:
    """stops a task, returns if it was successful"""
    name = name.lower()

    if not task_exist(name) or not task_running(name):
        return False

    task = get_task(name)
    task.cancel()

    del active_tasks[name]


def task_running(name: str):
    return task_exist(name) and not get_task(name).done()


async def _remove_done_tasks():
    global active_tasks

    while True:
        done_tasks = tuple(k for k, t in active_tasks.items() if t.done())
        for k in done_tasks:
            del active_tasks[k]

        await sleep(15)


get_event_loop().create_task(_remove_done_tasks())
