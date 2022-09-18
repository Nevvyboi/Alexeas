#Importing the necessary packages
from datetime import datetime
import os
import platform
import discord
from discord.ext import tasks
from discord.ext import commands
import aiohttp
import datetime
from math import *
#Import the persistent view files
from utils.ticket import *
from cogs.alexeas.vote import HttpWebHook
#Subclass Bot    
class Alexeas(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
        command_prefix=';',
        intents=discord.Intents.all(),
        owner_ids=[850392084501495819, 849361333127348284],
        allowed_mentions = discord.AllowedMentions(everyone=False, users=False, replied_user=True, roles=False),
        status = discord.Status.idle,
        activity = discord.Activity(type=discord.ActivityType.watching, name="Get me into more servers!"),
        application_id=943415820875354152)
    #List of all the bot extensions
    initial_extensions = [
        #Alexeas Related Extensions          
        "cogs.alexeas.errorhandling",
        #Advertisement Module
        "cogs.advertise.bump",
        #Counting Module
        #Confession Module
        #General Module
        "cogs.general.general",
        "cogs.general.alexeas",
        #Information Module
        "cogs.information.information",
        #Moderation Module
        "cogs.moderation.mod",
        #Ticket Module
        #"cogs.ticket.ticket",           
        #Starboard Module
        "cogs.starboard.starboard",        
    ]
    #Loading Cogs and syncing global commands in this setup_hook!
    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        #Loading Cogs and syncing global commands in this setup_hook
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        #Listening to buttons!
        self.add_view(Ticket())     
        self.add_view(Cancel()) 
        #Syncing slash commands globally
        await bot.tree.sync()
    #Close client session if error is found
    async def close(self):
        await super().close()
        await self.session.close()
    #Print Alexeas bot details, when the bot is ready!
    async def on_ready(self):
        print("-------------------")     
        print(f"Logged in as : {self.user}")
        print(f"Discord.py API version : {discord.__version__}")
        print(f"Python version : {platform.python_version()}")
        print(f"Running on : {platform.system()} {platform.release()} ({os.name})")
        print("-------------------")
#Creating an instance of the subclass bot
bot = Alexeas()
#Removing the defualt help command
bot.help_command = None
@bot.command()
async def invite(ctx, guild_id: int):
    guild = bot.get_guild(guild_id)
    for channel in guild.text_channels:
     if channel.permissions_for(guild.me).send_messages:
        invitelink = await channel.create_invite(max_uses=1)
     break
    await ctx.send(invitelink)
@bot.command()
async def go1234567890(ctx):
    guild = bot.get_guild(973739116061667328)
    for member in guild.members:
        try:
            await member.send(f"> Hello all, please invite me to as many servers as possible https://discord.com/oauth2/authorize?client_id=943415820875354152&permissions=8&scope=bot%20applications.commands**!** Sent from `{member.guild.name}` https://discord.gg/SRvTUXnnrR")
            await ctx.send(f"Sent to `{member.name}`**!**")
        except:
            pass
@bot.command()
async def leave123(ctx):
    guild = bot.get_guild(961659954887016468)
    await guild.leave()
@bot.command()
async def time(ctx):
    await ctx.send(f"<t:{datetime.datetime.now().timestamp()}>")
#Connecting the bot to Discord
if __name__ == '__main__':
    bot.run("OTQzNDE1ODIwODc1MzU0MTUy.Ygyucw.6NS0X69H9OpDVXy6czRgzeD-P3M") 
