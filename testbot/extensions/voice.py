import logging

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def voice(self, ctx):
        """Commands to manage voice functionality."""
        await ctx.send_help(self)

    @voice.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Join a voice channel."""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @voice.command()
    async def play(self, ctx, *, query):
        """Play a file from the local filesystem."""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {query}')

    @voice.command()
    async def stop(self, ctx):
        """Stop and disconnect the bot from voice."""

        await ctx.voice_client.disconnect()


def setup(bot):
    bot.add_cog(Voice(bot))
