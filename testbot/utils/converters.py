from discord.ext.commands import Context, Converter


class MessageConverter(Converter):
    async def convert(self, ctx: Context, arg: str):
        arg = int(arg)
        return await ctx.get_message(arg)
