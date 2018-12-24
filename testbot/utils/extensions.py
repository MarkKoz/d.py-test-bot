import logging
import os
from enum import Enum
from pkgutil import iter_modules
from traceback import StackSummary, TracebackException

from discord.ext.commands import Bot

from testbot.bot import TestBot

log = logging.getLogger(__name__)
EXTENSION_EXLCUDES = frozenset(os.environ.get('EXTENSION_EXCLUDES', '').split(','))


class Action(Enum):
    LOAD = (TestBot.load_extension,)
    UNLOAD = (TestBot.unload_extension,)
    RELOAD = (TestBot.unload_extension, TestBot.load_extension)


def manage(ext: str, action: Action, bot: Bot):
    verb = action.name.lower()
    success = False
    error = None

    if (
        (action is Action.LOAD and ext not in bot.extensions)
        or (action is Action.UNLOAD and ext in bot.extensions)
        or action is Action.RELOAD
    ):
        try:
            for func in action.value:
                func(bot, ext)
        except Exception as e:
            error = TracebackException.from_exception(e)
            # err_msg = ''.join(error.format_exception_only()).strip()
            # summary = StackSummary.from_list([error.stack[0]])
            log.error(
                f'Extension \'{ext}\' failed to {verb}:\n'
                + ''.join(error.format()).rstrip()
            )
            msg = f'Failed to load extension `{ext}`:\n```{e}```'
        else:
            log.debug(f'Extension \'{ext}\' succesfully {verb}ed.')
            msg = f'Extension {verb}ed: `{ext}`.'
    else:
        log.warning(f'Extension \'{ext}\' is already {verb}ed.')
        msg = f'Extension `{ext}` is already {verb}ed.'

    return msg, error


def get_extensions():
    for ext in iter_modules(('testbot/extensions',), 'testbot.extensions.'):
        if ext.name not in EXTENSION_EXLCUDES and ext.name[-1] != '_':
            yield ext.name


def qualify_extension(ext: str):
        ext = ext.lower()
        return ext if '.' in ext else 'testbot.extensions.' + ext
