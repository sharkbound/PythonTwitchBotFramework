from ..config import Config, CONFIG_FOLDER

__all__ = [
    'logging_config'
]

logging_config = Config(
    CONFIG_FOLDER / 'console_logging_config.json',
    log_privmsg=True,
    log_whisper=True,
    log_command_usage=True,
    log_whisper_sent=True,
    log_privmsg_sent=True,
)
