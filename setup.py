from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().split('\n')
    print(requirements)

setup(
    name='PythonTwitchBotFramework',
    version='1.0',
    packages=find_packages(),
    url='https://github.com/sharkbound/PythonTwitchBotFramework',
    license='MIT',
    author='sharkbound',
    description='asynchronous twitchbot framework made in pure python',
    install_requires=requirements,
)
