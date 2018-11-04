from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().split('\n')
    print(requirements)

setup(
    name='PythonTwitchBotFramework',
    version='1.0',
    packages=['twitchbot', 'twitchbot.api', 'twitchbot.bots', 'twitchbot.util', 'twitchbot.database'],
    url='https://github.com/sharkbound/PythonTwitchBotFramework',
    license='MIT',
    author='sharkbound',
    author_email='',
    description='async python twitchbot framework',
    install_requires=requirements
)
