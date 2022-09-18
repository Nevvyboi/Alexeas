#Importing the necessary packages
import aiosqlite
import discord
from discord import app_commands
from discord.app_commands import Choice, describe
from discord.ext import commands, tasks
import sqlite3
import datetime
from utils.confirm import *
from utils.emojis import *
from utils.module import *

class Starboard(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.module = "starSys"
        self.db = sqlite3.connect('Database/starboard.db')
        self.cursor = self.db.cursor()

    @commands.Cog.listener()
    async def on_ready(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS starboard(guild_id INTEGER, channel_id INTEGER, emoji TEXT, lim INTEGER)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS stars(message_id INTEGER, stars INTEGER, bot_id INTEGER, channel_id INTEGER, guild_id INTEGER)")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
     try:
         data = sqlite3.connect('Database/settings.db')
         cursor = data.cursor()  
         cursor.execute("SELECT starSys FROM Server WHERE guild = ?", (payload.guild_id,))
         sys = cursor.fetchone()
         if sys:
            if not sys[0] == 1:
                return 
         cursor.close()
         data.close()  
         db = await aiosqlite.connect('Database/starboard.db')
         cursor = await db.cursor()
         await cursor.execute(f"SELECT channel_id, emoji, lim FROM starboard WHERE guild_id = {payload.guild_id}")
         result = await cursor.fetchone()  
         if result is None:
             return
         elif result is not None:
             reactchannel = self.bot.get_channel(payload.channel_id)
             message = await reactchannel.fetch_message(payload.message_id)
             starchannel = self.bot.get_channel(result[0])
             await cursor.execute(f"SELECT message_id FROM stars WHERE message_id = {message.id}")
             i = await cursor.fetchone()
             try:
                 if result[1] is None:
                     staremoji = "⭐"
                 elif result[1] is not None:
                     staremoji = result[1]
                 if result[2] is None:
                     limit = 3
                 elif result[2] is not None:
                     limit = result[2]
             except:
                 pass
             if i is None:
              for i in message.reactions:
               if str(i.emoji) == staremoji and i.count >= limit and reactchannel.id != starchannel.id:
                em = discord.Embed(description=message.content + f"\n[Jump to message](https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id})", color=0x2f3136, timestamp=discord.utils.utcnow())
                em.set_author(name=F"{message.author} | Starred post", icon_url=message.author.avatar.url)
                em.set_footer(text=f"ID : {message.id}", icon_url=message.guild.icon.url)
                try:
                    if message.content.startswith('https://'):
                        em.set_image(url=message.content)
                except:
                    pass
                if message.attachments:
                    attach = message.attachments
                    em.set_image(url = attach[0].url)
                id = await starchannel.send(f"{limit} {staremoji} | {message.channel.mention}",embed=em)
                sql = "INSERT INTO stars(message_id, stars, bot_id, channel_id, guild_id) VALUES(?,?,?,?,?)"
                val = (message.id, limit, id.id, id.channel.id, payload.guild_id)
                await cursor.execute(sql, val)
                await db.commit()
             elif i is not None:
                i = i[0]
                await cursor.execute(f"SELECT stars, bot_id, channel_id FROM stars WHERE message_id = {message.id}")
                msg = await cursor.fetchone()
                if msg is None:
                 pass
                elif msg is not None:
                 channel = self.bot.get_channel(msg[2])
                 id = await channel.fetch_message(msg[1])
                 stars = msg[0]
                 stars = stars + 1
                 sql = "UPDATE stars SET stars = ? WHERE message_id = ?"
                 val = (stars, message.id)
                 await cursor.execute(sql, val)
                 await db.commit()
                 await id.edit(content=f"{stars} {staremoji} | {message.channel.mention}")
         await cursor.close()
         await db.close()
     except Exception as e:
         print(e)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
         data = sqlite3.connect('Database/settings.db')
         cursor = data.cursor()  
         cursor.execute("SELECT starSys FROM Server WHERE guild = ?", (payload.guild_id,))
         sys = cursor.fetchone()
         if sys:
            if not sys[0] == 1:
                return 
         cursor.close()
         data.close() 
         db = await aiosqlite.connect('Database/starboard.db')
         cursor = await db.cursor()
         await cursor.execute(f"SELECT channel_id, emoji FROM starboard WHERE guild_id = {payload.guild_id}")
         result = await cursor.fetchone()  
         if result is None:
             return
         elif result is not None:
             reactchannel = self.bot.get_channel(payload.channel_id)
             message = await reactchannel.fetch_message(payload.message_id)
             await cursor.execute(f"SELECT message_id FROM stars WHERE message_id = {message.id}")
             i = await cursor.fetchone()
             try:
                 if result[1] is None:
                     staremoji = "⭐"
                 elif result[1] is not None:
                     staremoji = result[1]
             except:
                 pass
             if i is None:
                 pass
             elif i is not None:
                i = i[0]
                await cursor.execute(f"SELECT stars, bot_id, channel_id FROM stars WHERE message_id = {message.id}")
                msg = await cursor.fetchone()
                if msg is None:
                 pass
                elif msg is not None:
                 channel = self.bot.get_channel(msg[2])
                 id = await channel.fetch_message(msg[1])
                 stars = msg[0]
                 stars = stars - 1
                 sql = "UPDATE stars SET stars = ? WHERE message_id = ?"
                 val = (stars, message.id)
                 await cursor.execute(sql, val)
                 await db.commit()
                 await id.edit(content=f"{stars} {staremoji} | {message.channel.mention}")
         await cursor.close()
         await db.close()

    group = app_commands.Group(name="starboard", description="Settings for the starboard module!", guild_only=True)

    @group.command(name="channel", description="Setting the starboard channel in your server!") # we use the declared group to make a command.
    @app_commands.describe(channel = 'The channel, where the starred messages will be posted!')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def channel(self, interaction: discord.Interaction, channel : discord.TextChannel) -> None:
        try:
         #Method to check if the module is disabled!
         check = await modulecheck(interaction, self.module)
         if check is False:
            return
         #Starboard Channel Code 
         self.cursor.execute(f"SELECT channel_id FROM starboard WHERE guild_id = {interaction.guild.id}")
         result = self.cursor.fetchone()
         view = Confirm(interaction)
         await interaction.response.send_message(f'{question} Are you sure you want to set {channel.mention} as the starboard channel**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
            if result is None:
                sql = ("INSERT INTO starboard(guild_id, channel_id) VALUES(?,?)")
                val = (interaction.guild.id, channel.id)
                await interaction.edit_original_message(content=f"{correct} Starboard channel has been set**!**")
            elif result is not None:
                sql = ("UPDATE starboard SET channel_id = ? WHERE guild_id = ?")
                val = (channel.id, interaction.guild.id)
                await interaction.edit_original_message(content=f"{correct} Starboard channel has been updated**!**")
         elif view.value is False:
            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
         elif view.timeout:
            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**")                 
         self.cursor.execute(sql, val)
         self.db.commit()
        except Exception as e:
            pass

    @group.command(name="emoji", description="Setting the starboard emoji in your server!") # we use the declared group to make a command.
    @app_commands.describe(emoji = 'The emoji needed for a message to be starred!')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def emoji(self, interaction: discord.Interaction, emoji : str) -> None:
        try:
         #Method to check if the module is disabled!
         check = await modulecheck(interaction, self.module)
         if check is False:
            return
         #Starboard Emoji Code 
         self.cursor.execute(f"SELECT emoji FROM starboard WHERE guild_id = {interaction.guild.id}")
         result = self.cursor.fetchone()
         view = Confirm(interaction)
         await interaction.response.send_message(f'{question} Are you sure you want to set the starboard emoji to {emoji}**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
            if result is None:
                sql = ("INSERT INTO starboard(guild_id, emoji) VALUES(?,?)")
                val = (interaction.guild.id, emoji)
                await interaction.edit_original_message(content=f"{correct} Starboard emoji has been set**!**")
            elif result is not None:
                sql = ("UPDATE starboard SET emoji = ? WHERE guild_id = ?")
                val = (emoji, interaction.guild.id)
                await interaction.edit_original_message(content=f"{correct} Starboard emoji has been updated**!**")
         elif view.value is False:
            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
         elif view.timeout:
            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**")
         self.cursor.execute(sql, val)
         self.db.commit()
        except Exception as e:
            pass

    @group.command(name="limit", description="Setting the starboard star limit in your server!") # we use the declared group to make a command.
    @app_commands.describe(limit = 'The star limit needed for a message to be starred!')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def limit(self, interaction: discord.Interaction, limit : int) -> None:
     try:
         #Method to check if the module is disabled!
         check = await modulecheck(interaction, self.module)
         if check is False:
            return
         #Starboard Limit Code 
         self.cursor.execute(f"SELECT lim FROM starboard WHERE guild_id = {interaction.guild.id}")
         result = self.cursor.fetchone()
         if limit <= 0:
                return await interaction.response.send_message(f"{wrong} The starboard emoji limit can not be less than 1**!**", ephemeral=True)             
         view = Confirm(interaction)
         await interaction.response.send_message(f'{question} Are you sure you want to set the emoji limit for the starboard to `{limit}`**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
            if result is None:
                sql = ("INSERT INTO starboard(guild_id, lim) VALUES(?,?)")
                val = (interaction.guild.id, limit)
                await interaction.edit_original_message(content=f"{correct} Starboard limit has been set**!**")
            elif result is not None:
                sql = ("UPDATE starboard SET lim = ? WHERE guild_id = ?")
                val = (limit, interaction.guild.id)
                await interaction.edit_original_message(content=f"{correct} Starboard limit has been updated**!**")
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
      self.cursor.execute(f"DELETE FROM starboard WHERE guild_id = {guild.id}")
      self.cursor.execute(f"DELETE FROM stars WHERE guild_id = {guild.id}")      
      self.db.commit()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
      self.cursor.execute(f"SELECT channel_id FROM starboard WHERE guild_id = {channel.guild.id}")
      result = self.cursor.fetchone() 
      try:
        result = result[0]
      except:
          pass
      if channel.id == result:
       self.cursor.execute(f"DELETE  FROM starboard WHERE guild_id = {channel.guild.id}")
       self.db.commit()
      else:
       pass

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(Starboard(bot))