from asyncio import Task

from sqlalchemy import Column, Integer, String, Float, Boolean

from .session import Base
from ..config import cfg
from ..enums import CommandContext

__all__ = ('Quote', 'CustomCommand', 'Balance', 'CurrencyName', 'MessageTimer', 'DBCounter')


class Quote(Base):
    __tablename__ = 'quotes'

    id = Column(Integer, primary_key=True, nullable=False)
    user = Column(String(255))
    channel = Column(String(255), nullable=False)
    alias = Column(String(255))
    value = Column(String(520), nullable=False)

    @classmethod
    def create(cls, channel: str, value: str, user: str = None, alias: str = None):
        return Quote(channel=channel.lower(), user=user, value=value, alias=alias)


class CustomCommand(Base):
    __tablename__ = 'commands'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    channel = Column(String(255), nullable=False)
    response = Column(String(520), nullable=False)
    context = CommandContext.CHANNEL
    permission = None

    @classmethod
    def create(cls, channel: str, name: str, response: str):
        return CustomCommand(channel=channel.lower(), name=name.lower(), response=response)

    @property
    def fullname(self):
        return self.name

    def __str__(self):
        return f'<CustomCommand channel={self.channel!r} name={self.name!r} response={self.response!r}>'


class Balance(Base):
    __tablename__ = 'balance'

    id = Column(Integer, nullable=False, primary_key=True)
    channel = Column(String(255), nullable=False)
    user = Column(String(255), nullable=False)
    balance = Column(Integer, nullable=False)

    @classmethod
    def create(cls, channel: str, user: str, balance: int = cfg.default_balance):
        return Balance(channel=channel.lower(), user=user, balance=balance)


class CurrencyName(Base):
    __tablename__ = 'currency_names'

    id = Column(Integer, nullable=False, primary_key=True)
    channel = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)

    @classmethod
    def create(cls, channel: str, name: str):
        return CurrencyName(channel=channel.lower(), name=name)


class MessageTimer(Base):
    __tablename__ = 'message_timers'

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(255), nullable=False)
    channel = Column(String(255), nullable=False)
    message = Column(String(520), nullable=False)
    interval = Column(Float, nullable=False)
    active = Column(Boolean, nullable=False, default=False)
    task: Task = None

    @property
    def running(self):
        return self.task is not None and not self.task.done()

    @classmethod
    def create(cls, channel: str, name: str, message: str, interval: float, active=False):
        return MessageTimer(name=name, channel=channel, message=message, interval=interval, active=active)

class DBCounter(Base):
    __tablename__ = 'counter'

    id = Column(Integer, primary_key=True, nullable=False)
    user = Column(String(255))
    channel = Column(String(255), nullable=False)
    alias = Column(String(255))
    value = Column(Integer, nullable=False)

    @classmethod
    def create(cls, channel: str, value: int = 0, user: str = None, alias: str = None):
        return DBCounter(channel=channel.lower(), user=user, value=value, alias=alias)
    
    def __str__(self):
        return f'{self.alias} -> {self.value}'