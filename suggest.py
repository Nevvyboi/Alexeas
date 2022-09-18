#Importing the necessary packages
import discord
from discord import Permissions, app_commands
from discord.app_commands import Choice, describe
from discord.ext import commands
import sqlite3
import datetime
from utils.confirm import Confirm
from utils.emojis import *
from utils.module import *
from utils.suggestion import *
        
class Suggestion(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.module = "suggestionSys"
        self.db = sqlite3.connect('Database/main.db')
        self.cursor = self.db.cursor()

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect('Database/main.db')
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS suggest(guild_id INTEGER, channel_id INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS blacklist(user INTEGER, guild_id INTEGER)")

    @app_commands.command(name = 'suggest', description = 'Make a suggestion in the server!')
    @app_commands.describe(suggestion = 'The message you wish to suggest!') 
    @app_commands.checks.bot_has_permissions(send_messages=True)  
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
    async def suggest(self, interaction : discord.Interaction , suggestion : str, image : discord.Attachment = None) -> None:
     try:
        #Method to check if the module is disabled!
        check = await modulecheck(interaction, self.module)
        if check is False:
            return
        #Method to check if user is banned from using this command!
        check = await bancheck(interaction)
        if check is False:
            return
        #Suggest Code
        self.cursor.execute(f"SELECT channel_id FROM suggest WHERE guild_id = {interaction.guild.id}")
        result = self.cursor.fetchone()
        if result is None:
                await interaction.response.send_message(f"{wrong} Suggestion channel not set**!**", ephemeral=True)   
        elif result[0] is None:
                await interaction.response.send_message(f"{wrong} Suggestion channel not set**!**", ephemeral=True) 
        else:       
                channel = self.bot.get_channel(result[0])
                await interaction.response.send_message(f"{correct} Suggestion has been submitted**!**", ephemeral=True)
                embed = discord.Embed(colour=interaction.user.color.random(), description=f"• {suggestion}", timestamp=discord.utils.utcnow())
                embed.set_author(icon_url=interaction.guild.icon.url, name=f"Suggestion  ~ by {interaction.user}")
                embed.set_footer(text="Use /suggest to make a suggestion")
                embed.set_thumbnail(url=interaction.user.avatar.url)
                if image is None:
                    pass
                else:
                    embed.set_image(url=image)
                msg = await channel.send(embed=embed)
                await msg.add_reaction(correct)
                await msg.add_reaction(wrong)   
     except Exception as e:
        pass         

    group = app_commands.Group(name="suggestion", description="Settings for the /suggest command!", guild_only=True)

    @group.command(name="channel", description="Setting the suggestion channel in your server!") # we use the declared group to make a command.
    @app_commands.describe(channel = 'The channel, where the suggestion will be posted!')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def channel(self, interaction: discord.Interaction, channel : discord.TextChannel) -> None:
        try:
         #Method to check if the module is disabled!
         check = await modulecheck(interaction, self.module)
         if check is False:
            return
         #Suggestion Channel Code 
         view = Confirm(interaction)
         self.cursor.execute(f"SELECT channel_id FROM suggest WHERE guild_id = {interaction.guild.id}")
         result = self.cursor.fetchone()
         await interaction.response.send_message(f'{question} Are you sure you want to set {channel.mention} as the suggestion channel**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
            if result is None:
                sql = ("INSERT INTO suggest(guild_id, channel_id) VALUES(?,?)")
                val = (interaction.guild.id, channel.id)
                await interaction.edit_original_message(content=f"{correct} Suggestion channel has been set**!**")
            elif result is not None:
                sql = ("UPDATE suggest SET channel_id = ? WHERE guild_id = ?")
                val = (channel.id, interaction.guild.id)
                await interaction.edit_original_message(content=f"{correct} Suggestion channel has been updated**!**")
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
      self.cursor.execute(f"DELETE FROM suggest WHERE guild_id = {guild.id}")
      self.cursor.execute(f"DELETE FROM blacklist WHERE guild_id = {guild.id}")
      self.db.commit()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
      self.cursor.execute(f"SELECT channel_id FROM suggest WHERE guild_id = {channel.guild.id}")
      result = self.cursor.fetchone() 
      try:
        result = result[0]
      except:
          pass
      if channel.id == result:
       self.cursor.execute(f"DELETE  FROM suggest WHERE guild_id = {channel.guild.id}")
       self.db.commit()
      else:
       pass

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(Suggestion(bot))