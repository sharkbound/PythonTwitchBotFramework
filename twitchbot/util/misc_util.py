from glob import glob
from pathlib import Path
from typing import List
import os


def get_py_files(path: str) -> List[str]:
    """gets all python (.py) files in a folder"""
    yield from glob(os.path.join(path, '*.py'))


def get_file_name(path: str):
    """gets the files name without the extension"""
    return os.path.basename(path).split('.')[0]
