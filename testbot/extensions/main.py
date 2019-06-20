import io
import json
import logging

import discord
from discord.ext import commands

from testbot.utils import MessageConverter

log = logging.getLogger(__name__)


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def avatar(self, ctx):
        async with self.bot.session.get(self.bot.user.avatar_url) as r:
            content = await r.read()
            await self.bot.user.edit(avatar=content)
            await ctx.send(r.status)

    @commands.command(name="embed_info")
    async def embed_info(self, ctx, message: MessageConverter):
        for embed in message.embeds:
            await ctx.send(json.dumps(embed.to_dict()))

    @commands.command()
    async def relay(self, ctx):
        log.info(ctx.message.content)

    @commands.command()
    async def image(self, ctx, image_url: str):
        async with self.bot.session.get(image_url) as resp:
            image = await resp.read()
            image = io.BytesIO(image)
            await ctx.send(file=discord.File(image, filename="image.gif"))


def setup(bot):
    bot.add_cog(Main(bot))
