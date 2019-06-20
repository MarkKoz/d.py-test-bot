import logging
from textwrap import dedent

from discord.ext.commands import Cog, Context, group

from testbot.utils import extensions

log = logging.getLogger(__name__)
UNLOAD_BLACKLIST = ('testbot.extensions.manager',)


class Extensions(Cog):
    def __init__(self, bot):
        self.bot = bot

    @group(name='extensions', aliases=('e', 'ext'), invoke_without_command=True)
    async def extensions_group(self, ctx: Context):
        await ctx.invoke(self.bot.get_command('help'), 'extensions')

    @extensions_group.command(name='load', aliases=('l',))
    async def load_command(self, ctx: Context, ext: str):
        ext = extensions.qualify_extension(ext)
        msg, _ = extensions.manage(ext, extensions.Action.LOAD, self.bot)
        await ctx.send(msg)

    @extensions_group.command(name='unload', aliases=('u', 'ul'))
    async def unload_command(self, ctx: Context, ext: str):
        ext = extensions.qualify_extension(ext)

        if ext in UNLOAD_BLACKLIST:
            log.warning(f'Extension \'{ext}\' is blacklisted from unloading.')
            msg = f'Extension \'{ext}\' may not be unloaded.'
        else:
            msg, _ = extensions.manage(ext, extensions.Action.UNLOAD, self.bot)

        await ctx.send(msg)

    @extensions_group.command(name='reload', aliases=('r',))
    async def reload_command(self, ctx: Context, ext: str):
        if ext.startswith('*'):
            unloaded = []
            unload_failures = {}
            load_failures = {}

            to_unload = self.bot.extensions.copy().keys()
            for extension in to_unload:
                _, error = extensions.manage(extension, extensions.Action.UNLOAD, self.bot)
                if error:
                    unload_failures[extension] = error
                else:
                    unloaded.append(extension)

            if ext == '**':
                unloaded = extensions.get_extensions()

            for extension in unloaded:
                _, error = extensions.manage(extension, extensions.Action.LOAD, self.bot)
                if error:
                    load_failures[extension] = error

            msg = dedent(f'''
                **All extensions reloaded**
                Unloaded: `{len(to_unload) - len(unload_failures)}`/`{len(to_unload)}`
                Loaded: `{len(unloaded) - len(load_failures)}`/`{len(unloaded)}`
            ''').strip()

            if unload_failures:
                failures = '\n'.join(f'{ext}\n    {err}' for ext, err in unload_failures)
                msg += f'\nUnload failures:```{failures}```'

            if load_failures:
                failures = '\n'.join(f'{ext}\n    {err}' for ext, err in load_failures)
                msg += f'\nLoad failures:```{failures}```'

            log.debug(f'Reloaded all extensions.')
        else:
            ext = extensions.qualify_extension(ext)
            msg, _ = extensions.manage(ext, extensions.Action.RELOAD, self.bot)

        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Extensions(bot))
