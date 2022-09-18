#Importing the necessary packages
from urllib import response
import discord
from discord import Permissions, app_commands
from discord.app_commands import Choice, describe
from discord.ext import commands
import sqlite3
import datetime
import random
from utils.confirm import *
from utils.emojis import *
from utils.module import *
from utils.confession import *
        
class Confession(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.module = "confessionSys"
        self.db = sqlite3.connect('Database/main.db')
        self.cursor = self.db.cursor()

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect('Database/main.db')
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS confess(guild_id INTEGER, channel_id INTEGER, log_id INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS blacklist(user INTEGER, guild_id INTEGER)")

    @app_commands.command(name = 'confess', description = 'Make a confession in the server!')
    @app_commands.describe(confession = 'The message you wish to confess!') 
    @app_commands.checks.bot_has_permissions(send_messages=True) 
    @app_commands.guild_only() 
    @app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
    async def confess(self, interaction : discord.Interaction , confession : str) -> None:
     try:
        #Method to check if the module is disabled!
        check = await modulecheck(interaction, self.module)
        if check is False:
            return
        #Method to check if user is banned from using this command!
        check = await bancheck(interaction)
        if check is False:
            return
        #Confess Code  
        self.cursor.execute(f"SELECT channel_id FROM confess WHERE guild_id = {interaction.guild.id}")
        result = self.cursor.fetchone()
        if result is None:
            await interaction.response.send_message(f"{wrong} Confession channel not set**!**", ephemeral=True)
        elif result[0] is None:
            await interaction.response.send_message(f"{wrong} Confession channel not set**!**", ephemeral=True)             
        else:
            c = discord.Color.random()
            channel = self.bot.get_channel(result[0])
            await interaction.response.send_message(f"{correct} Confession sent**!**", ephemeral=True)
            embed = discord.Embed(timestamp=discord.utils.utcnow(),colour=c, description=f"• *{confession}*")
            embed.set_author(icon_url=interaction.guild.icon.url, name=f"Confession ~ Anonymous")
            embed.set_footer(text="Use /confess to make a confession")
            l = await channel.send(embed=embed)
            try:
                link = l.jump_url
                self.cursor.execute(f"SELECT log_id FROM confess WHERE guild_id = {interaction.guild.id}")
                log = self.cursor.fetchone()    
                if log is None:
                    pass
                else:
                    channel1 = self.bot.get_channel(log[0])  
                    embed = discord.Embed(timestamp=discord.utils.utcnow(),colour=c, description=f"• {interaction.user.name} ({interaction.user.mention})\n• *{confession}*\n• [Jump to Confession]({link})")
                    embed.set_author(icon_url=interaction.guild.icon.url, name=f"Confession ~ Logs")
                    embed.set_footer(text="Use /confess to make a confession")
                    embed.set_thumbnail(url=interaction.user.avatar.url)
                    await channel1.send(embed=embed)
            except Exception as e:
                pass       
     except Exception as e:
      pass

    group = app_commands.Group(name="confession", description="Settings for the /confess command!",guild_only=True)

    @group.command(name="channel", description="Setting the confession channel in your server!") # we use the declared group to make a command.
    @app_commands.describe(channel = 'The channel, where the confession will be posted!')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def channel(self, interaction: discord.Interaction, channel : discord.TextChannel) -> None:
       try:
         #Method to check if the module is disabled!
         check = await modulecheck(interaction, self.module)
         if check is False:
            return
         #Confession Channel Code   
         view = Confirm(interaction)
         self.cursor.execute(f"SELECT channel_id FROM confess WHERE guild_id = {interaction.guild.id}")
         result = self.cursor.fetchone()
         await interaction.response.send_message(f'{question} Are you sure you want to set {channel.mention} as the confession channel**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
            if result is None:
                sql = ("INSERT INTO confess(guild_id, channel_id) VALUES(?,?)")
                val = (interaction.guild.id, channel.id )
                await interaction.edit_original_message(content=f"{correct} Confession channel has been set**!**")
            elif result is not None:
                sql = ("UPDATE confess SET channel_id = ? WHERE guild_id = ?")
                val = (channel.id, interaction.guild.id)
                await interaction.edit_original_message(content=f"{correct} Confession channel has been updated**!**")
         elif view.value is False:
            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
         elif view.timeout:
            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**") 
         self.cursor.execute(sql, val)
         self.db.commit()
       except Exception as e:
        pass

    @group.command(name="logs", description="Setting the confession logs channel in your server!") # we use the declared group to make a command.
    @app_commands.describe(channel = 'The channel, where the confession logs will be posted!')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def logs(self, interaction: discord.Interaction, channel : discord.TextChannel) -> None:
       try:
         #Method to check if the module is disabled!
         check = await modulecheck(interaction, self.module)
         if check is False:
            return
         #Confession Logs Code 
         view = Confirm(interaction)
         self.cursor.execute(f"SELECT log_id FROM confess WHERE guild_id = {interaction.guild.id}")
         result = self.cursor.fetchone()
         await interaction.response.send_message(f'{question} Are you sure you want to set {channel.mention} as the confession log channel**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
            if result is None:
                sql = ("INSERT INTO confess(guild_id, log_id) VALUES(?,?)")
                val = (interaction.guild.id, channel.id )
                await interaction.edit_original_message(content=f"{correct} Confession logs channel has been set**!**")
            elif result is not None:
                sql = ("UPDATE confess SET log_id = ? WHERE guild_id = ?")
                val = (channel.id, interaction.guild.id)
                await interaction.edit_original_message(content=f"{correct} Confession logs channel has been updated**!**")
         elif view.value is False:
            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
         elif view.timeout:
            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**") 
         self.cursor.execute(sql, val)
         self.db.commit()
       except Exception as e:
        pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
     try:
      self.cursor.execute(f"DELETE FROM confess WHERE guild_id = {guild.id}")
      self.cursor.execute(f"DELETE FROM blacklist WHERE guild_id = {guild.id}")
      self.db.commit()
     except Exception as e:
      pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
     try:
      self.cursor.execute(f"SELECT channel_id FROM confess WHERE guild_id = {channel.guild.id}")
      result = self.cursor.fetchone() 
      try:
        result = result[0]
      except:
          pass
      if channel.id == result:
       self.cursor.execute(f"DELETE  FROM confess WHERE guild_id = {channel.guild.id}")
       self.db.commit()
      else:
       pass
     except Exception as e:
      pass

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(Confession(bot))