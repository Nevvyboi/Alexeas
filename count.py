#Importing the necessary packages
import discord
from discord import Permissions, app_commands
from discord.app_commands import Choice, describe
from discord.ext import commands
import sqlite3
import pandas
from number_parser import parse_number
from utils.emojis import *
from utils.confirm import *
import aiosqlite
from utils.module import *

class Counting(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.module = "countSys"
        self.db = sqlite3.connect('Database/main.db')
        self.cursor = self.db.cursor()

    @commands.Cog.listener()
    async def on_message(self, message):
     try:
            data = sqlite3.connect('Database/settings.db')
            cursor = data.cursor()  
            cursor.execute("SELECT countSys FROM Server WHERE guild = ?", (message.guild.id,))
            sys = cursor.fetchone()
            if sys:
                if not sys[0] == 1:
                    return  
            db = await aiosqlite.connect('Database/main.db')
            cursor = await db.cursor()                               
            await cursor.execute(f"SELECT * FROM count WHERE guild_id = ?", (message.guild.id,))
            result = await cursor.fetchone()
            if result is None:
                pass
            elif result is not None:
                if message.channel.id != result[1]:
                    return
                if message.author.bot:
                    return
                cnum = result[3] + 1
                if message.author.id == result[2]:
                    await message.delete()
                    await message.channel.send(f"`{message.author.name}` You can't count twice in a row**!**", delete_after = 5)
                else:
                    msg = message.content
                    try:
                        result = pandas.eval(msg)
                        val = True
                    except:
                        val = False
                    if val is True:
                        newnumber = result
                        if newnumber == cnum:
                            await message.add_reaction(correct)
                            count = cnum
                            await cursor.execute(f"UPDATE count SET last_user = {message.author.id}, count = {count} WHERE guild_id = {message.guild.id}")
                        elif newnumber != cnum:
                            await message.add_reaction(wrong)
                            await message.channel.send(f"`{message.author.name}` The next number is `{cnum}`**!**")
                    elif val is False:
                        if str(cnum) in message.content:
                            await message.add_reaction(correct)
                            count = cnum
                            await cursor.execute(f"UPDATE count SET last_user = {message.author.id}, count = {count} WHERE guild_id = {message.guild.id}")
                        elif str(cnum) not in message.content:
                            await message.add_reaction(wrong)
                            await message.channel.send(f"`{message.author.name}` The next number is `{cnum}`**!**")                                                        
            await db.commit()
     except Exception as e:
         pass
         
    group = app_commands.Group(name="counting", description="Settings for the counting module!", guild_only=True)

    @group.command(name="channel", description="Setting the counting channel in your server!") # we use the declared group to make a command.
    @app_commands.describe(channel = 'The channel, where you will count!')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def channel(self, interaction: discord.Interaction, channel : discord.TextChannel) -> None:
       try:
         #Method to check if the module is disabled!
         check = await modulecheck(interaction, self.module)
         if check is False:
             return
         #Counting Channel Code
         view = Confirm(interaction)
         self.cursor.execute(f"SELECT channel_id FROM count WHERE guild_id = {interaction.guild.id}")
         result = self.cursor.fetchone()
         await interaction.response.send_message(f'{question} Are you sure you want to set {channel.mention} as the counting channel**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
            if result is None:
                sql = ("INSERT INTO count(guild_id, channel_id, last_user , count) VALUES(?,?,?,?)")
                val = (interaction.guild.id, channel.id , 943415820875354152,  0)
                await interaction.edit_original_message(content=f"{correct} Counting channel has been set**!**")   
                await channel.edit(slowmode_delay=3) 
            elif result is not None:
                sql = ("UPDATE count SET channel_id = ? WHERE guild_id = ?")
                val = (channel.id, interaction.guild.id)
                await interaction.edit_original_message(content=f"{correct} Counting channel has been updated**!**")     
                await channel.edit(slowmode_delay=3)    
         elif view.value is False:
            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
         elif view.timeout:
            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**")
         self.cursor.execute(sql, val)
         self.db.commit()
       except Exception as e:
        print(e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
     try:
      self.cursor.execute(f"DELETE FROM count WHERE guild_id = {guild.id}")
      self.db.commit()
     except Exception as e:
      pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
     try:
      self.cursor.execute(f"SELECT channel_id FROM count WHERE guild_id = {channel.guild.id}")
      result = self.cursor.fetchone() 
      result = result[0]
      if channel.id == result:
       self.cursor.execute(f"DELETE  FROM count WHERE guild_id = {channel.guild.id}")
       self.db.commit()
     except Exception as e:
      pass

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(Counting(bot))