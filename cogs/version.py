from utils.update import get_commits_for, get_url_for_hash
from utils.message import error_embed, info_embed
import utils.variables as variables
import utils.classes as classes

from discord.ext import commands
import datetime
import logging

logger = logging.getLogger()
ets2la_asset = classes.get_asset_with_name("ETS2LA", variables.ASSET_URLS)
class version(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def version(self, ctx: commands.Context, version: str = None):
        """
        Lookup a specific version of ETS2LA by it's shortened hash.
        """
        if version is None:
            await ctx.send(embed=error_embed("Please provide a version hash to lookup."))
            logger.info(f"[bold]{ctx.author.name}[/bold] did not provide a version hash for the version command")
            return
        
        target_hash = version
        commits = get_commits_for(ets2la_asset)
        if len(commits) == 0:
            await ctx.send(embed=error_embed("Failed to fetch ETS2LA commits."))
            logger.warning(f"[bold]{ctx.author.name}[/bold] failed to fetch ETS2LA commits for the version command")
            return
        
        for commit in commits:
            if commit.hexsha.startswith(target_hash):
                commit_time = datetime.datetime.fromtimestamp(commit.committed_date)
                
                commit_title = commit.message.split("\n")[0]
                commit_description = commit.message.split("\n")[1:]
                commit_description = "\n".join(commit_description)
                
                embed_description = f"**Author:** `{commit.author.name}`"
                embed_description += f"\n**Time:** `{commit_time}`"
                embed_description += f"\n\n**Message:**\n```{commit_title}\n{commit_description}```"
                    
                await ctx.send(embed=info_embed(f"{get_url_for_hash(commit.hexsha, ets2la_asset)}", embed_description))
                logger.info(f"[bold]{ctx.author.name}[/bold] provided a valid version hash for the version command: `{version}`")
                return
        
        await ctx.send(embed=error_embed("Failed to find the specified version hash."))
        logger.info(f"[bold]{ctx.author.name}[/bold] provided an invalid version hash for the version command: `{version}`")

async def setup(bot: commands.Bot):
    await bot.add_cog(version(bot))