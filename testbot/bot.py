import asyncio
import logging
import socket
import warnings
from typing import Optional

import aiohttp
import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class TestBot(commands.Bot):
    """A Bot with an aiohttp session and custom `wait_until_guild_available`."""

    def __init__(self, guild: int, *args, **kwargs):
        if "connector" in kwargs:
            warnings.warn(
                'If login() is called (or the bot is started), '
                'the connector will be overwritten with an internal one'
            )

        super().__init__(*args, **kwargs)

        self.http_session: t.Optional[aiohttp.ClientSession] = None
        self.guild = guild

        self._connector = None
        self._resolver = None
        self._guild_available = asyncio.Event()

    async def on_ready(self):
        log.info(
            f'{self.description} logged in as {self.user} ({self.user.id}).'
        )

    async def on_resumed(self):
        log.info(f'{self.description} resumed.')

    async def on_message(self, msg: discord.Message):
        if not msg.author.bot:
            await self.process_commands(msg)

    def clear(self) -> None:
        """
        Clear internal state of the bot and recreate the connector and sessions.

        Will cause a DeprecationWarning if called outside a coroutine.
        """
        # Because discord.py recreates the HTTPClient session, may as well
        # follow suit and recreate our own stuff here too.
        self._recreate()
        super().clear()

    async def close(self) -> None:
        """Close the session, connector, resolver, and Discord connection."""
        await super().close()

        if self.http_session:
            await self.http_session.close()

        if self._connector:
            await self._connector.close()

        if self._resolver:
            await self._resolver.close()

    async def login(self, *args, **kwargs) -> None:
        """Re-create the connector, set up session, then log into Discord."""
        self._recreate()
        await super().login(*args, **kwargs)

    def _recreate(self) -> None:
        """Re-create the connector, aiohttp session, and the APIClient."""
        # Use asyncio for DNS resolution instead of threads so threads aren't
        # spammed.
        # Doesn't seem to have any state with regards to being closed,
        # so no need to worry?
        self._resolver = aiohttp.AsyncResolver()

        # Its __del__ does send a warning but it doesn't always show up
        # for some reason.
        if self._connector and not self._connector._closed:
            log.warning(
                'The previous connector was not closed; '
                'it will remain open and be overwritten'
            )

        # Use AF_INET as its socket family to prevent HTTPS related problems
        # both locally and in production.
        self._connector = aiohttp.TCPConnector(
            resolver=self._resolver,
            family=socket.AF_INET,
        )

        # Client.login() will call HTTPClient.static_login() which will create a
        # session using this connector attribute.
        self.http.connector = self._connector

        # Its __del__ does send a warning but it doesn't always show up
        # for some reason.
        if self.http_session and not self.http_session.closed:
            log.warning(
                'The previous session was not closed; '
                'it will remain open and be overwritten'
            )

        self.http_session = aiohttp.ClientSession(connector=self._connector)

    async def on_guild_available(self, guild: discord.Guild) -> None:
        """Set guild available event when `self.guild` becomes available."""
        if guild.id == self.guild:
            self._guild_available.set()

    async def on_guild_unavailable(self, guild: discord.Guild) -> None:
        """Clear guild available event when `self.guild` becomes unavailable."""
        if guild.id == self.guild:
            self._guild_available.clear()

    async def wait_until_guild_available(self) -> None:
        """
        Wait until the `self.guild` guild is available (and the cache is ready).
        The on_ready event is inadequate because it only waits 2 seconds for a
        GUILD_CREATE gateway event before giving up and thus not populating the
        cache for unavailable guilds.
        """
        await self._guild_available.wait()
