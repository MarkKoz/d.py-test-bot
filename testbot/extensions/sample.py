import logging
from typing import List

from discord.ext import commands


log = logging.getLogger(__name__)


class Config:
    my_channel: int = 400121469641818124
    my_category: int = 400121469641818123
    my_role: int = 400499713570242571
    my_voice: int = 647317854978310157
    my_webhook: int = 690000402552455210

    enabled: bool = True
    role_whitelist: List[int] = [400499713570242571, 400121903420801033]


class Sample(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command("getcfg")
    async def get_config(self, ctx):
        log.debug(Config.my_category)
        log.debug(Config.my_channel)
        log.debug(Config.my_role)
        log.debug(Config.my_voice)
        log.debug(Config.my_webhook)

        log.debug(Config.enabled)
        log.debug(Config.role_whitelist)


def setup(bot):
    bot.add_cog(Sample(bot))
