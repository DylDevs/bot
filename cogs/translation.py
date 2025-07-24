import utils.classes as classes
from utils.update import *
from utils.message import *

from discord.ext import commands, tasks
import datetime
import discord
import logging
import yaml
import sys
import os

logger = logging.getLogger()
translations_asset = classes.get_asset_with_name("Translations", variables.ASSET_URLS)
translations_repo = translations_asset.path
class translation(commands.Cog):
    keys = None
    
    @tasks.loop(minutes=10)
    async def update_repo_task(self):
        await update_repo(translations_asset)
        
        files = os.listdir(translations_repo)
        
        self.old_keys = self.keys
        self.languages = []
        self.keys = []
        self.translations = {}
        for file in files:
            if file.endswith(".yaml"):
                if not file.startswith("keys"):
                    with open(f"{translations_repo}/{file}", "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        self.translations[data["Language"]["name_en"]] = data["Translations"]
                        self.languages.append(data["Language"])
                else:
                    with open(f"{translations_repo}/{file}", "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        self.keys = data
            
        if self.old_keys and self.old_keys != self.keys:
            new_keys = [key for key in self.keys if key not in self.old_keys]
            removed_keys = [key for key in self.old_keys if key not in self.keys]
            messages = []
            messages.append("<@&1271896625438003320>" + f"\n-# Update found on <t:{int(datetime.datetime.now().timestamp())}>")
            
            if new_keys:
                message = "### New keys found.\nThese are translations that haven't been in the app before.\n\n"
                message += "```diff\n"
                for key in new_keys:
                    message += f"+ {key}\n"
                message += "```"
                messages.append(message)
            if removed_keys:
                message = "### Removed keys found.\nThese are translations that have been removed from the app.\n\n"
                message += "```diff\n"
                for key in removed_keys:
                    message += f"- {key}\n"
                message += "```"
                messages.append(message)
                
            if new_keys or removed_keys:
                for message in messages:
                    await self.bot.get_channel(variables.TRANSLATION_UPDATE_CHANNEL).send(message)
    
    def __init__(self, bot):
        self.bot = bot
        self.update_repo_task.start()

    async def list(self, ctx: commands.Context, type: str):
        if type == "languages":
            languages = ""
            for language in self.languages:
                languages += f"- {language['name_en']} ({language['iso_code']})\n"
            await ctx.send(embed=info_embed("Available languages", languages))
            logger.info(f"[bold]{ctx.author.name}[/bold] requested the translation languages list")
        elif type == "keys":
            keys_text = "Unfortunately there are too many keys to list here. \
                        We've attached the `keys.yaml` file for you to download and view."
            await ctx.send(embed=info_embed("Available keys", keys_text), file=discord.File(f"{translations_repo}/keys.yaml"))
            logger.info(f"[bold]{ctx.author.name}[/bold] requested the translation keys list")
        else:
            await ctx.send(embed=error_embed("Invalid type provided, please use either `languages` or `keys`"))
            logger.info(f"[bold]{ctx.author.name}[/bold] provided an invalid type for the translation list command: `{type}`")

    async def status(self, ctx: commands.Context, language: str):
        if not language or language == "":
            await ctx.send(embed=error_embed("Please provide a language to lookup"))
            logger.info(f"[bold]{ctx.author.name}[/bold] did not provide a language for the translation status command")
            return
            
        if language not in self.translations and language != "all":
            await ctx.send(embed=error_embed("The specified language was not found"))
            logger.info(f"[bold]{ctx.author.name}[/bold] provided an invalid language for the translation status command: `{language}`")
            return
        
        languages = self.translations.keys() if language == "all" else [language]
        
        embeds = []
        for i, language in enumerate(languages):
            total_keys = len(self.keys) - 5 # Remove the language keys
            extra_keys = 0
            keys_found = 0
            for key in self.translations[language]:
                if key in self.keys:
                    keys_found += 1
                else:
                    extra_keys += 1
            
            description = f"**Total keys:** {total_keys}\n"
            description += f"**Keys translated:** {keys_found}/{total_keys} ({round(keys_found / total_keys * 100, 1)}%)\n"
            description += f"**Extra keys:** {extra_keys}"
            embed = success_embed(description, f"{language}")
            embeds.append(embed)

            if len(embeds) == 10: # Max of 10 embeds per message
                await ctx.send(embeds=embeds)
                embeds = []
            
        await ctx.send(embeds=embeds)
        logger.info(f"[bold]{ctx.author.name}[/bold] requested the translation status for {language}")

    async def translate(self, ctx: commands.Context, language: str, key: str):
        if not language or language == "":
            await ctx.send(embed=error_embed("Please provide a language to translate to"))
            logger.info(f"[bold]{ctx.author.name}[/bold] did not provide a language for the translate command")
            return
            
        if not key or key == "":
            await ctx.send(embed=error_embed("Please provide a key to translate"))
            logger.info(f"[bold]{ctx.author.name}[/bold] did not provide a key for the translate command")
            return
            
        if language not in self.translations:
            await ctx.send(embed=error_embed("The specified language was not found"))
            logger.info(f"[bold]{ctx.author.name}[/bold] provided an invalid language for the translate command: `{language}`")
            return
        
        if key not in self.keys:
            await ctx.send(embed=error_embed("The specified key was not found"))
            logger.info(f"[bold]{ctx.author.name}[/bold] provided an invalid key for the translate command: `{key}`")
            return
        
        english = self.translations["English"][key]
        translation = self.translations[language][key]
        await ctx.send(embed=success_embed(f"Translation for `{english}` in `{language}`", translation))
        logger.info(f"[bold]{ctx.author.name}[/bold] requested the translation for `{key}` in `{language}`, result: `{translation}`")

    @commands.command(name="translation")
    async def translation(self, ctx: commands.Context, command: str = None, *args):
        """Broken don't use."""
        if not command or command == "":
            await ctx.send(embed=error_embed("Please provide a command to lookup (use `help` for a list)"))
            logger.info(f"[bold]{ctx.author.name}[/bold] did not provide a command for the translation command")
            return
        
        if command == "help":
            available_commands = "- `help` - Show this message\n"
            available_commands += "- `list { languages OR keys }` - List all available languages or keys\n"
            available_commands += "- `status { language_en OR all }` - Get the translation status of a language (or all of them)\n"
            available_commands += "- `translate {language_en} {key}` - Translate a key to a language\n"
            await ctx.send(embed=info_embed("Available commands", available_commands))
            logger.info(f"[bold]{ctx.author.name}[/bold] requested the translation help command")
            return
        
        if command == "list":
            await self.list(ctx, args[0] if len(args) > 0 else "")
            
        if command == "status":
            await self.status(ctx, " ".join(args))
            
        if command == "translate":
            await self.translate(ctx, args[0], args[1])

async def setup(bot: commands.Bot):
    await bot.add_cog(translation(bot))