from setuptools import setup, find_packages
from twitchbot import BOT_VERSION

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    long_description = f.read()

setup(
    name='PythonTwitchBotFramework',
    version='.'.join(map(str, BOT_VERSION)),
    python_requires='>=3.6',
    packages=find_packages() + ['twitchbot.builtin_translations', 'twitchbot.builtin_commands'],
    url='https://github.com/sharkbound/PythonTwitchBotFramework',
    license='MIT',
    author='sharkbound',
    description='asynchronous twitch-bot framework made in pure python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    scripts=[
        'util/command_console.py',
    ],
    include_package_data=True
)