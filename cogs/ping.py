from discord.ext import commands
import datetime
import discord
import logging

logger = logging.getLogger()

class ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context, member: discord.Member = None):
        """
        Ping the bot to check its responsiveness.
        """
        if member is None:
            member = ctx.author
        
        time = datetime.datetime.now() - ctx.message.created_at.replace(tzinfo=None)
        await ctx.send(f"pong!\n-# in {time.microseconds / 1000:.0f}ms")
        logger.info(f"[bold]{member.name}[/bold] pinged the bot in {time.microseconds / 1000:.0f}ms")

async def setup(bot: commands.Bot):
    await bot.add_cog(ping(bot))