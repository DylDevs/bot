from utils.message import error_embed, success_embed
import utils.variables as variables

from discord.ext import commands, tasks
import datetime
import logging
import os

logger = logging.getLogger()

if os.path.exists(variables.VERIFIED_USERS_FILE):
    with open(variables.VERIFIED_USERS_FILE, "r") as f:
        verified_users = [int(line.strip()) for line in f.readlines()]
else:
    os.makedirs(os.path.dirname(variables.VERIFIED_USERS_FILE), exist_ok=True)
    with open(variables.VERIFIED_USERS_FILE, "w") as f:
        f.write("")
        verified_users = []
        
def save_verified():    
    with open(variables.VERIFIED_USERS_FILE, "w") as f:
        for user in verified_users:
            f.write(f"{user}\n")

class verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.save_verified_task.start()

    @tasks.loop(minutes=1)
    async def save_verified_task(self):
        save_verified()

    def has_link(self, message):
        links = ["https://", "http://", "www.", ".com", ".net", ".org"]
        excluded_links = ["discord.gg", "discordapp.com", "discord.com", "tenor.com", "giphy.com", "youtube.com", "twitch.tv", "youtu.be", "ets2la.com"]
        return any(link in message.content for link in links) and not any(excluded in message.content for excluded in excluded_links)
    
    def has_money(self, message):
        return any(symbol in message.content for symbol in ["$", "€", "£", "¥", "₹", "dollar"])
    
    def has_steam(self, message):
        steam = ["steam", "steamcommunity", "steampowered"]
        excluded_steam = ["workshop", "steamid", "steamid3", "steamid64"]
        return any(steam_word in message.content for steam_word in steam) and not any(excluded_steam_word in message.content for excluded_steam_word in excluded_steam)

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        if author.id in verified_users or author.bot:
            return
        
        has_money = self.has_money(message)
        has_link = self.has_link(message)
        has_steam = self.has_steam(message)
        
        if has_money or has_link or has_steam:
            text = "<@&1132519946799284315> "
            text += "Please check the user manually. "
            text += "They were flagged because of:"
            if has_money:
                text += "\n- First message contains money related terms."
                logger.info(f"[{author.name}] was flagged as a possible scammer because of money related terms")
            if has_link:
                text += "\n- First message contains links."
                logger.info(f"[{author.name}] was flagged as a possible scammer because of links")
            if has_steam:
                text += "\n- First message references *Steam*."
                logger.info(f"[{author.name}] was flagged as a possible scammer because of Steam references")
                
            await message.reply(embed=error_embed(text, title="Possible scammer detected"))
            await author.timeout(datetime.timedelta(days=1), reason="Possible scammer detected")
        else:
            await message.reply(embed=success_embed("Your first message indicates no signs of potential scamming.\n-# You might see this message multiple times due to updates to the verification system.", title="Verified"), delete_after=5)
            verified_users.append(author.id)
            logger.info(f"[{author.name}] was verified")

async def setup(bot: commands.Bot):
    await bot.add_cog(verify(bot))