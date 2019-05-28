import os
import sys
from contextlib import contextmanager
from datetime import datetime
from glob import iglob
from typing import List

__all__ = ('get_py_files', 'get_file_name', 'temp_syspath', 'format_datetime')


def get_py_files(path: str) -> List[str]:
    """gets all python (.py) files in a folder"""
    yield from iglob(os.path.join(path, '*.py'))


def format_datetime(dt: datetime) -> str:
    return dt.strftime('%d/%m/%Y %H:%M:%S')


def get_file_name(path: str):
    """gets the files name without the extension"""
    return os.path.basename(path).split('.')[0]


@contextmanager
def temp_syspath(fullpath):
    """
    temporarily appends the fullpath to sys.path, yields, then removes it from sys.path
    if the fullpath is already in sys.path the append/remove is skipped
    """
    if not os.path.isabs(fullpath):
        fullpath = os.path.abspath(fullpath)

    if fullpath not in sys.path:
        sys.path.insert(0, fullpath)
        yield
        sys.path.remove(fullpath)
    else:
        yield
