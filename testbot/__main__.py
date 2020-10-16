import logging
import os

import discord

from testbot.config import load_config
from testbot.bot import TestBot
from testbot.utils import extensions

log = logging.getLogger('testbot')
bot = TestBot(
    guild=int(os.environ['GUILD']),
    command_prefix='!',
    description='Discord.py Test Bot',
    pm_help=None,
    help_attrs=dict(hidden=True),
    intents=discord.Intents.all()
)

EXTENSION_EXLCUDES = frozenset(os.environ.get('EXTENSION_EXCLUDES', '').split(','))
for extension in extensions.EXTENSIONS:
    if extension not in EXTENSION_EXLCUDES:
        bot.load_extension(extension)

load_config(bot)

bot.run(os.environ['BOT_TOKEN'])
