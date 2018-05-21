from asyncio import Future, Task

from sqlalchemy import Column, Integer, String, Float, Boolean

from config import cfg
from enums import CommandContext
from .session import Base, database_init

__all__ = ('Quote', 'CustomCommand')


class Quote(Base):
    __tablename__ = 'quotes'

    id = Column(Integer, primary_key=True, nullable=False)
    user = Column(String)
    channel = Column(String, nullable=False)
    alias = Column(String)
    value = Column(String, nullable=False)

    @classmethod
    def create(cls, channel: str, value: str, user: str = None, alias: str = None):
        return Quote(channel=channel.lower(), user=user, value=value, alias=alias)


class CustomCommand(Base):
    __tablename__ = 'commands'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    response = Column(String, nullable=False)
    context = CommandContext.CHANNEL

    @classmethod
    def create(cls, channel: str, name: str, response: str):
        return CustomCommand(channel=channel.lower(), name=name.lower(), response=response)

    def __str__(self):
        return f'<CustomCommand channel={self.channel!r} name={self.name!r} response={self.response!r}>'


class Balance(Base):
    __tablename__ = 'balance'

    id = Column(Integer, nullable=False, primary_key=True)
    channel = Column(String, nullable=False)
    user = Column(String, nullable=False)
    balance = Column(Integer, nullable=False)

    @classmethod
    def create(cls, channel: str, user: str, balance: int = cfg.default_balance):
        return Balance(channel=channel.lower(), user=user, balance=balance)


class CurrencyName(Base):
    __tablename__ = 'currency_names'

    id = Column(Integer, nullable=False, primary_key=True)
    channel = Column(String, nullable=False)
    name = Column(String, nullable=False)

    @classmethod
    def create(cls, channel: str, name: str):
        return CurrencyName(channel=channel.lower(), name=name)


class MessageTimer(Base):
    __tablename__ = 'message_timers'

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    message = Column(String, nullable=False)
    interval = Column(Float, nullable=False)
    active = Column(Boolean, nullable=False, default=False)
    task: Task = None

    @property
    def running(self):
        return self.task is not None and not self.task.done()

    @classmethod
    def create(cls, channel: str, name: str, message: str, interval: float, active=False):
        return MessageTimer(name=name, channel=channel, message=message, interval=interval, active=active)


database_init()
