import logging
import traceback

import discord
from aiohttp import ClientSession
from discord.ext import commands

log = logging.getLogger(__name__)


class TestBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            description='Discord.py Rewrite Test Bot',
            pm_help=None,
            help_attrs=dict(hidden=True)
        )

        self.session = None

    async def on_ready(self):
        log.info(
            f'{self.description} logged in as {self.user} ({self.user.id}).'
        )

    async def on_resumed(self):
        log.info(f'{self.description} resumed.')

    async def on_message(self, msg: discord.Message):
        if not msg.author.bot:
            await self.process_commands(msg)

    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError
    ):
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
                f'{ctx.command.qualified_name} failed to execute. '
                f'{error.original.__class__.__name__}: {error.original}\n'
                f'{"".join(traceback.format_tb(error.original.__traceback__))}'
            )

    async def start(self, *args, **kwargs):
        self.session = ClientSession()
        await super().start(*args, **kwargs)

    async def close(self):
        await self.session.close()
        await super().close()
