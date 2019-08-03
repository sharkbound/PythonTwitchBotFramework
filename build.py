from os import system
from pathlib import Path
from shutil import rmtree
from sys import executable

build = Path('build')
dist = Path('dist')
egg = Path('PythonTwitchBotFramework.egg-info')


def delete_build_folders():
    if build.exists():
        rmtree(build)
    if dist.exists():
        rmtree(dist)
    if egg.exists():
        rmtree(egg)


delete_build_folders()
system(f'{executable} setup.py sdist bdist_wheel')
system('twine upload dist/*')
if input('remove build folders? [Y/N]: ').lower().strip() == 'y':
    delete_build_folders()
