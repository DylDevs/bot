from discord.ext import commands
from utils.message import success_embed, error_embed
import datetime
import logging

logger = logging.getLogger()

class time(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def time(self, ctx: commands.Context, timezone: str = None):
        """
        Time in Tumppi066's timezone. Optionally type an offset in hours.
        """
        if timezone is None:
            # Convert to EEST (Eastern European Summer Time)
            local_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)
            await ctx.send(embed=success_embed(f"Tumppi066's current local time is {local_time.strftime('%H:%M:%S')}"))
        else:
            try:
                # Convert to specified timezone
                local_time = datetime.datetime.now(datetime.timezone.utc).astimezone(tz=datetime.timezone(datetime.timedelta(hours=int(timezone))))
                await ctx.send(embed=success_embed(f"Current time in that timezone is **{local_time.strftime('%H:%M:%S')}**"))
            except ValueError:
                await ctx.send(embed=error_embed("Invalid timezone specified. Please use a valid offset in hours (e.g., +3 for EEST)."))

async def setup(bot: commands.Bot):
    await bot.add_cog(time(bot))