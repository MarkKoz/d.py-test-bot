import asyncio
import json
import logging

import discord
from discord.ext import commands

from testbot.utils import MessageConverter

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

    @commands.command(name="embed_info")
    async def embed_info(self, ctx, message: MessageConverter):
        for embed in message.embeds:
            await ctx.send(json.dumps(embed.to_dict()))


def setup(bot):
    bot.add_cog(Main(bot))
