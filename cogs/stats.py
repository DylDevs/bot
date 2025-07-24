from utils.message import success_embed, error_embed
import utils.variables as variables

from discord.ext import commands
import requests
import datetime
import discord
import logging

logger = logging.getLogger()

class stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = None
        self.login()

    def active_users(self):
        response = requests.get(f"{variables.STATS_API}/active", headers={
            "Authorization": f"Bearer {self.token}"
        })
        return response.json()["x"]

    def get_stats(self):
        url = f"{variables.STATS_API}/stats"
        url += "?startAt=" + str(int(datetime.datetime.now().timestamp() * 1000) - 86400000)
        url += "&endAt=" + str(int(datetime.datetime.now().timestamp() * 1000))
        url += "&unit=hour&timezone=Europe%2FHelsinki&compare=false"
        
        response = requests.get(url, 
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        try:
            return response.json()
        except:
            return response.text
    
    def login(self):
        if self.token is not None:
            return
        
        response = requests.post(f"{variables.UMAMI_API}/auth/login", data={
            "username": variables.ENV.UMAMI_LOGIN, 
            "password": variables.ENV.UMAMI_PASS
        })
        
        self.token = response.json()["token"]
        logger.info("Logged in to Unami API")

    @commands.command("stats")
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def stats(self, ctx: commands.Context, member: discord.Member = None):
        if member is None:
            member = ctx.author
        
        active_users = self.active_users()
        
        stats = self.get_stats()
        if type(stats) != dict:
            await ctx.send(embed=error_embed(f"Something went wrong while fetching the stats.\n```{stats}```"))
            logger.warning(f"Something went wrong while fetching stats from the Umami API:\n{stats}")
            return
        
        pageviews = stats["pageviews"]["value"]
        visitors = stats["visitors"]["value"]
        visits = stats["visits"]["value"]
        bounces = stats["bounces"]["value"]
        bounce_rate = bounces / visits * 100
        total_time = stats["totaltime"]["value"] / 60 / 60
        
        title = f"{active_users} currently active users"
        
        description = "Stats for the last 24 hours:\n"
        description += f"- Pageviews: {pageviews}\n"
        description += f"- Visitors: {visitors}\n"
        description += f"- Visits: {visits}\n"
        description += f"- Bounces: {bounces}\n"
        description += f"- Bounce rate: {bounce_rate:.2f}%\n"
        description += f"- Total time: {total_time:.0f} hours"
        
        await ctx.send(embed=success_embed(description, title))
        logger.info(f"[bold]{member.name}[/bold] requested stats")

async def setup(bot: commands.Bot):
    await bot.add_cog(stats(bot))