import logging

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    """Handler for discord.py errors."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError
    ):
        """Handle errors caused by commands."""
        # Skips errors that were already handled locally.
        if getattr(ctx, 'handled', False):
            return

        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command cannot be used in direct messages.')
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send('Too many arguments.')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Missing required argument `{error.param.name}`.')
        elif (
            isinstance(error, commands.NotOwner)
            or isinstance(error, commands.MissingPermissions)
        ):
            await ctx.send(
                'You do not have the required permissions to invoke this '
                'command.'
            )
        elif (
            isinstance(error, commands.CommandOnCooldown)
            or isinstance(error, commands.CheckFailure)
        ):
            await ctx.send(error)
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(
                'This command is currently disabled and cannot be used.'
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f'Bad argument: {error}')
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                'Oops! The bot does not have the required permissions to '
                'execute this command.'
            )
            log.error(
                f'{ctx.command.qualified_name} cannot be executed because the '
                f'bot is missing the following permissions: '
                f'{", ".join(error.list)}'
            )
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('Something went wrong internally!')
            log.error(
                f'{ctx.command.qualified_name} failed to execute. ',
                exc_info=error.original
            )

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
