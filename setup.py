from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().split('\n')

with open('README.md') as f:
    long_description = f.read()

setup(
    name='PythonTwitchBotFramework',
    version='1.0.1',
    packages=find_packages(),
    url='https://github.com/sharkbound/PythonTwitchBotFramework',
    license='MIT',
    author='sharkbound',
    description='asynchronous twitch-bot framework made in pure python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    scripts=[
        'command_console.py',
    ]
)
