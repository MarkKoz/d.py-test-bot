import logging
import os

import discord

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

for extension in extensions.get_extensions():
    extensions.manage(extension, extensions.Action.LOAD, bot)

bot.run(os.environ['BOT_TOKEN'])
