from discord.ext import commands
import discord
import logging

logger = logging.getLogger()

class xdd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def xdd(self, ctx: commands.Context, member: discord.Member = None):
        """
        :xdx:
        """
        if member is None:
            member = ctx.author
        
        await ctx.send(f"<:xdx:1195115294696415352>")
        logger.info(f"[bold]{member.name}[/bold] used the xdd command")

async def setup(bot: commands.Bot):
    await bot.add_cog(xdd(bot))