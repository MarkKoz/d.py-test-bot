import logging

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class Main:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def avatar(self, ctx):
        async with bot.session.get(bot.user.avatar_url) as r:
            content = await r.read()
            await bot.user.edit(avatar=content)
            await ctx.send(r.status)


def setup(bot):
    bot.add_cog(Main(bot))
