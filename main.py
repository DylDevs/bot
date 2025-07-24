# Setup logger first to prevent discordpy from hijacking it
from utils.logger import setup_global_logging
logger = setup_global_logging()

from utils.message import error_embed, success_embed, cooldown_embed, info_embed
from utils.update import update_repo
import utils.variables as variables

from discord.ext import commands
import traceback

bot = commands.Bot(
    command_prefix=variables.PREFIX, 
    intents=variables.INTENTS
)
cogs = [
    "ping",
    "version",
    "stats",
    "translation",
    "xdd",
    "update_watcher",
    "verify",
    "time",
    "support"
]

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    for cog in cogs:
        try:
            await bot.load_extension(f"cogs.{cog}")
            logger.info(f"Loaded the {cog} extension")
        except Exception as e:
            logger.error(f"Failed to load the {cog} extension:\n{traceback.format_exc()}")
    
@bot.event
async def on_command_error(ctx, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=error_embed("The specified command was not found."))
    elif isinstance(error, commands.CommandOnCooldown):
        await cooldown_embed(ctx, error)
    else:
        await ctx.send(embed=error_embed(f"The command ran into an error.\n```{error}```"))
        trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        logger.error(f"Command ran into an error:\n{trace}")
        
@bot.command("update")
async def update_repo_command(ctx: commands.Context, repo: str):
    author = ctx.author
    if author.id not in variables.ENV.ADMINS:
        logger.info(f"[bold]{author.name}[/bold] attempted to run the update command without permission on [bold]{repo}[/bold]")
        await ctx.send(embed=error_embed("You do not have permission to run this command."))
        return
    else:
        logger.info(f"[bold]{author.name}[/bold] ran the update command on [bold]{repo}[/bold]")
    
    message = await ctx.send(embed=info_embed(f"Updating {repo}", "This may take a while."))
    await update_repo(repo)
    await message.edit(embed=success_embed(f"{repo} has been updated to the newest version on github."))
    
@bot.command("reload")
async def reload(ctx: commands.Context, *target_cogs):
    global cogs

    # Ensure user has permission
    author = ctx.author
    if author.id not in variables.ENV.ADMINS:
        logger.info(f"[bold]{author.name}[/bold] ({author.id}) attempted to run the reload command without permission")
        await ctx.send(embed=error_embed("You do not have permission to run this command."))
        return
    else:
        logger.info(f"[bold]{author.name}[/bold] ran the reload command")

    # Define variables
    cogs = cogs if not target_cogs else target_cogs
    amount = len(cogs)
    embeds = []

    # Create initial embed messages
    for i, cog in enumerate(cogs):
        embeds.append(info_embed("Reloading", f"Reloading the `{cog}` extension ({i + 1}/{amount})"))

    # Reload extensions and update embeds with results
    message = await ctx.send(embeds=embeds)
    for i, cog in enumerate(cogs):
        try:
            await bot.reload_extension(f"cogs.{cog}")
            embeds[i] = success_embed(f"Successfully reloaded the `{cog}` extension ({i + 1}/{amount})")
            logger.info(f"Successfully reloaded the [bold]{cog}[/bold] extension")
        except Exception as e:
            embeds[i] = error_embed(f"Failed to reload the `{cog}` extension ({i + 1}/{amount})\n```{e}```")
            if isinstance(e, commands.errors.ExtensionNotLoaded):
                logger.info(f"Failed to reload the [bold]{cog}[/bold] extension: The extension was not loaded")
            else:
                logger.error(f"Failed to reload the [bold]{cog}[/bold] extension:\n{traceback.format_exc()}")
        message = await message.edit(embeds=embeds)
        
# Turn off Discord logging
bot.run(variables.ENV.CLIENT_TOKEN, log_handler=None)