import os

import asyncio
import logging

from testbot.bot import TestBot
from testbot.utils import extensions

log = logging.getLogger('testbot')
bot = TestBot()

for extension in extensions.get_extensions():
    extensions.manage(extension, extensions.Action.LOAD, bot)

bot.run(os.environ['BOT_TOKEN'])
