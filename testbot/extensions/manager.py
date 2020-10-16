import functools
import logging
import typing as t
from enum import Enum

from discord.ext import commands
from discord.ext.commands import Context, group

from testbot import extensions as exts
from testbot.bot import TestBot
from testbot.utils.extensions import EXTENSIONS, unqualify

log = logging.getLogger(__name__)


UNLOAD_BLACKLIST = {f"{exts.__name__}.manager"}
BASE_PATH_LEN = len(exts.__name__.split("."))


class Action(Enum):
    """Represents an action to perform on an extension."""

    # Need to be partial otherwise they are considered to be function definitions.
    LOAD = functools.partial(TestBot.load_extension)
    UNLOAD = functools.partial(TestBot.unload_extension)
    RELOAD = functools.partial(TestBot.reload_extension)


class Extension(commands.Converter):
    """
    Fully qualify the name of an extension and ensure it exists.

    The * and ** values bypass this when used with the reload command.
    """

    async def convert(self, ctx: Context, argument: str) -> str:
        """Fully qualify the name of an extension and ensure it exists."""
        # Special values to reload all extensions
        if argument == "*" or argument == "**":
            return argument

        argument = argument.lower()

        if argument in EXTENSIONS:
            return argument
        elif (qualified_arg := f"{exts.__name__}.{argument}") in EXTENSIONS:
            return qualified_arg

        matches = []
        for ext in EXTENSIONS:
            if argument == unqualify(ext):
                matches.append(ext)

        if len(matches) > 1:
            matches.sort()
            names = "\n".join(matches)
            raise commands.BadArgument(
                f":x: `{argument}` is an ambiguous extension name. "
                f"Please use one of the following fully-qualified names.```\n{names}```"
            )
        elif matches:
            return matches[0]
        else:
            raise commands.BadArgument(f":x: Could not find the extension `{argument}`.")


class Extensions(commands.Cog):
    """Extension management commands."""

    def __init__(self, bot: TestBot):
        self.bot = bot

    @group(name="extensions", aliases=("ext", "exts", "c", "cogs"), invoke_without_command=True)
    async def extensions_group(self, ctx: Context) -> None:
        """Load, unload, reload, and list loaded extensions."""
        await ctx.send_help(ctx.command)

    @extensions_group.command(name="load", aliases=("l",))
    async def load_command(self, ctx: Context, *extensions: Extension) -> None:
        r"""
        Load extensions given their fully qualified or unqualified names.

        If '\*' or '\*\*' is given as the name, all unloaded extensions will be loaded.
        """  # noqa: W605
        if not extensions:
            await ctx.send_help(ctx.command)
            return

        if "*" in extensions or "**" in extensions:
            extensions = set(EXTENSIONS) - set(self.bot.extensions.keys())

        msg = self.batch_manage(Action.LOAD, *extensions)
        await ctx.send(msg)

    @extensions_group.command(name="unload", aliases=("ul",))
    async def unload_command(self, ctx: Context, *extensions: Extension) -> None:
        r"""
        Unload currently loaded extensions given their fully qualified or unqualified names.

        If '\*' or '\*\*' is given as the name, all loaded extensions will be unloaded.
        """  # noqa: W605
        if not extensions:
            await ctx.send_help(ctx.command)
            return

        blacklisted = "\n".join(UNLOAD_BLACKLIST & set(extensions))

        if blacklisted:
            msg = f":x: The following extension(s) may not be unloaded:```{blacklisted}```"
        else:
            if "*" in extensions or "**" in extensions:
                extensions = set(self.bot.extensions.keys()) - UNLOAD_BLACKLIST

            msg = self.batch_manage(Action.UNLOAD, *extensions)

        await ctx.send(msg)

    @extensions_group.command(name="reload", aliases=("r",), root_aliases=("reload",))
    async def reload_command(self, ctx: Context, *extensions: Extension) -> None:
        r"""
        Reload extensions given their fully qualified or unqualified names.

        If an extension fails to be reloaded, it will be rolled-back to the prior working state.

        If '\*' is given as the name, all currently loaded extensions will be reloaded.
        If '\*\*' is given as the name, all extensions, including unloaded ones, will be reloaded.
        """  # noqa: W605
        if not extensions:
            await ctx.send_help(ctx.command)
            return

        if "**" in extensions:
            extensions = EXTENSIONS
        elif "*" in extensions:
            extensions = set(self.bot.extensions.keys()) | set(extensions)
            extensions.remove("*")

        msg = self.batch_manage(Action.RELOAD, *extensions)

        await ctx.send(msg)

    def batch_manage(self, action: Action, *extensions: str) -> str:
        """
        Apply an action to multiple extensions and return a message with the results.

        If only one extension is given, it is deferred to `manage()`.
        """
        if len(extensions) == 1:
            msg, _ = self.manage(action, extensions[0])
            return msg

        verb = action.name.lower()
        failures = {}

        for extension in extensions:
            _, error = self.manage(action, extension)
            if error:
                failures[extension] = error

        emoji = ":x:" if failures else ":ok_hand:"
        msg = f"{emoji} {len(extensions) - len(failures)} / {len(extensions)} extensions {verb}ed."

        if failures:
            failures = "\n".join(f"{ext}\n    {err}" for ext, err in failures.items())
            msg += f"\nFailures:```{failures}```"

        log.debug(f"Batch {verb}ed extensions.")

        return msg

    def manage(self, action: Action, ext: str) -> t.Tuple[str, t.Optional[str]]:
        """Apply an action to an extension and return the status message and any error message."""
        verb = action.name.lower()
        error_msg = None

        try:
            action.value(self.bot, ext)
        except (commands.ExtensionAlreadyLoaded, commands.ExtensionNotLoaded):
            if action is Action.RELOAD:
                # When reloading, just load the extension if it was not loaded.
                return self.manage(Action.LOAD, ext)

            msg = f":x: Extension `{ext}` is already {verb}ed."
            log.debug(msg[4:])
        except Exception as e:
            if hasattr(e, "original"):
                e = e.original

            log.exception(f"Extension '{ext}' failed to {verb}.")

            error_msg = f"{e.__class__.__name__}: {e}"
            msg = f":x: Failed to {verb} extension `{ext}`:\n```{error_msg}```"
        else:
            msg = f":ok_hand: Extension successfully {verb}ed: `{ext}`."
            log.debug(msg[10:])

        return msg, error_msg

    # This cannot be static (must have a __func__ attribute).
    async def cog_command_error(self, ctx: Context, error: Exception) -> None:
        """Handle BadArgument errors locally to prevent the help command from showing."""
        if isinstance(error, commands.BadArgument):
            await ctx.send(str(error))
            error.handled = True


def setup(bot: TestBot) -> None:
    """Load the Extensions cog."""
    bot.add_cog(Extensions(bot))
