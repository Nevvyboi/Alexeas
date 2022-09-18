#Importing the necessary packages
from typing import Optional
import discord
from discord import Interaction, Permissions, app_commands
from discord.app_commands import Choice, describe
from discord.ext import commands
import datetime
import sqlite3
import random
from discord.ext import tasks
from utils.confirm import *
from utils.emojis import *
from utils.module import *
from utils.advertise import *

class Bump(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.module = "advertiseSys"
        self.db = sqlite3.connect("Database/bump.db")
        self.cursor = self.db.cursor()
        self.autobump.start()

    @commands.Cog.listener()
    async def on_ready(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS bump(guild_id INTEGER, channel_id INTEGER, invite_url TEXT, description TEXT, new_bump TEXT, last_bump TEXT, last_user INTEGER)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tags(guild_id, community BOOL, anime BOOL, music BOOL, technology BOOL, gaming BOOL, education BOOL, entertainment BOOL, advertisement BOOL, social BOOL)")

    def cog_unload(self):
        self.autobump.cancel()

    @tasks.loop(minutes=1)
    async def autobump(self):
        self.cursor.execute("SELECT guild_id, last_bump FROM bump WHERE last_bump IS NOT NULL")
        results = self.cursor.fetchall()
        for result in results:
            rn = datetime.datetime.now()
            now = datetime.datetime.fromtimestamp(int(result[1]))
            if rn > now:
                self.cursor.execute(f'UPDATE bump SET new_bump = NULL, last_bump = NULL, last_user = NULL WHERE guild_id = {result[0]}')
        self.db.commit()

    @app_commands.command(name = 'bump', description = 'Advertise your server across multiple servers!')
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(create_instant_invite=True) 
    async def bump(self, interaction : discord.Interaction):
     try:  
        #Method to check if the module is disabled!
        check = await modulecheck(interaction, self.module)
        if check is False:
            return
        #Bump Code
        self.cursor.execute(f"SELECT * FROM bump WHERE guild_id = ?", (interaction.guild.id,))
        result = self.cursor.fetchone()
        tag = []
        self.cursor.execute(f"SELECT * FROM tags WHERE guild_id = ?", (interaction.guild.id,))
        tags = self.cursor.fetchone()
        if tags is None:
            tag = "No tag(s)"
        elif tags is not None:
            if tags[1] == 1:
                tag.append("Community")
            if tags[2] == 1:
                tag.append("Anime")         
            if tags[3] == 1:
                tag.append("Music")
            if tags[4] == 1:
                tag.append("Technology")   
            if tags[5] == 1:
                tag.append("Gaming")
            if tags[6] == 1:
                tag.append("Education")     
            if tags[7] == 1:
                tag.append("Entertainment")  
            if tags[8] == 1:
                tag.append("Social")                 
            tag = ", ".join(tag)                             
        if result is None:
            result = None
        elif result is not None:
            result = list(result)
        if result is None:
            description = None
        elif result is not None:
            description = result[3]
        la = interaction.guild.preferred_locale
        creation_date = round(interaction.guild.created_at.timestamp())
        embed = discord.Embed(color=0x2f3136, timestamp=discord.utils.utcnow(), description= f"{crown} __**Owner:**__ [{interaction.guild.owner}](https://discord.com/users/{interaction.guild.owner_id})\n{tada} __**Creation:**__ <t:{creation_date}:f> (<t:{creation_date}:R>)\n🆔 __**ID:**__ `{interaction.guild.id}`\n{lang} __**Language:**__ {langs[str(la)]}\n🏷️ __**Tag(s):**__ {tag}")
        embed.add_field(inline=False, name ='\u200b',value = description or 'No server description set**!**')  
        embed.set_thumbnail(url=interaction.guild.icon.with_size(1024))              
        embed.set_author(icon_url=interaction.guild.icon.url, name=interaction.guild.name)           
        embed.add_field(inline=False, name=f"{members} Members", value=f"`{interaction.guild.member_count}`")
        embed.set_footer(icon_url=interaction.user.display_avatar.url, text =f"Bumped by {interaction.user.name}")
        #Getting Server Emojis
        if interaction.guild.emojis is None:
            pass
        elif interaction.guild.emojis is not None:
            emojis = []
            i = 0
            for emoji in interaction.guild.emojis:
                i = i +1
                if i == 15:
                    break
                if emoji.animated:
                    emojis.append(f"<a:{emoji.name}:{emoji.id}>")
                else:
                    emojis.append(f"<:{emoji.name}:{emoji.id}>") 
            emojis = "".join(emojis)   
            embed.add_field(inline=False, name=f"{discicon} Emojis `{len(interaction.guild.emojis)}`", value=emojis or "No emojis")
        if result is None:
            link = await interaction.channel.create_invite(max_age = 0)
            link = str(link)  
        elif result is not None:
            link = result[2]           
        view = discord.ui.View()       
        item = discord.ui.Button(style=discord.ButtonStyle.gray, label=f"Join {interaction.guild.name}",url=link)  # Create an item to pass into the view class.
        view.add_item(item=item)
        #Finding channels to send the ad to
        channels = [results[0] for results in self.cursor.execute("SELECT channel_id FROM bump WHERE channel_id IS NOT NULL")]
        if result is None:
            result1 = None
        elif result is not None:
            result1 = result[1]
        if result1 is not None:
            channels.remove(result[1])
        #Removing it when there is more than 5 servers
        if len(channels) == 2:
            channels = random.sample(channels, 2)
        else:
            channels = random.sample(channels, 5)
        #Checking if the server is on bump cooldown
        if result is None:
            result4 = None
        elif result is not None:
            result4 = result[4]
        if result4 is None:
            now = datetime.datetime.now()
            if result1 is None:
                bump = "This server can bump every 6 hours"
                msg = f"{correct} Bump successful**!** Decrease `{interaction.guild.name}` cooldown by `2` hours by setting a advertisement channel**!**\nDo `/advertise channel`**!**"
                later = datetime.timedelta(hours=6)
            elif result1 is not None:
                bump = "This server can bump every 4 hours"
                msg = f"{correct} Bump successful**!**"
                later = datetime.timedelta(hours=4)    
            #Adding the time for the next bump after a successful bump           
            time = now  + later
            time = time.timestamp()
            time = round(time)
            time1 = round(datetime.datetime.now().timestamp())
            if result is None:
                sql = "INSERT INTO bump(guild_id, invite_url, new_bump, last_bump, last_user) VALUES(?,?,?,?,?)"
                val = (interaction.guild.id, link, time1, time, interaction.user.id)
            elif result is not None:
                sql = f"UPDATE bump SET new_bump = ?, last_bump = ?, last_user = ? WHERE guild_id = ?"
                val = (time1, time, interaction.user.id, interaction.guild.id)
            self.cursor.execute(sql, val)
            self.db.commit()
            #Displaying bumped message
            views = discord.ui.View()
            item = discord.ui.Button(style=discord.ButtonStyle.gray, label=f"Official Server",url="https://discord.gg/SRvTUXnnrR") 
            item1 = discord.ui.Button(style=discord.ButtonStyle.gray, label=f"Upvote",url="https://top.gg/bot/943415820875354152/vote") 
            views.add_item(item)
            views.add_item(item1)
            embed1 = discord.Embed(color=interaction.user.color, timestamp = discord.utils.utcnow(), description=msg)
            embed1.set_footer(icon_url=interaction.guild.icon.url, text= bump)
            await interaction.response.send_message(embed=embed1, view=views)
            #Sending server ad to shuffled server channels
            for ids in channels:    
                if self.bot.get_channel(ids) == None:
                    pass
                else:             
                    await self.bot.get_channel(ids).send(embed=embed, view=view)                
        elif result4 is not None:
            views = discord.ui.View()
            item = discord.ui.Button(style=discord.ButtonStyle.gray, label=f"Official Server",url="https://discord.gg/SRvTUXnnrR") 
            item1 = discord.ui.Button(style=discord.ButtonStyle.gray, label=f"Upvote",url="https://top.gg/bot/943415820875354152/vote") 
            views.add_item(item)
            views.add_item(item1)
            embed = discord.Embed(color=interaction.user.color, description=f"{wrong} Last bump made by `{self.bot.get_user(result[6])}` at <t:{result[4]}:f>", timestamp=discord.utils.utcnow())
            embed.add_field(inline=True, name="Next Bump", value = f"<t:{result[5]}:f> (<t:{result[5]}:R>)")
            return await interaction.response.send_message(embed=embed, view=views,ephemeral=True)
     except Exception as e:
        print(e)

    group = app_commands.Group(name="advertise", description="Settings for bumping your server!", guild_only=True)

    @group.command(name="channel", description="Recieve ads from other servers!") # we use the declared group to make a command.
    @app_commands.describe(channel = 'The channel, where you will recieve adverts from other servers!')
    @app_commands.checks.has_permissions(manage_guild=True) 
    async def channel(self, interaction: discord.Interaction, channel : discord.TextChannel) -> None:
       try:
         #Method to check if the module is disabled!
         check = await modulecheck(interaction, self.module)
         if check is False:
             return
         #Advertise Channel Code
         db = sqlite3.connect('Database/bump.db')
         cursor = db.cursor()
         cursor.execute(f"SELECT * FROM bump WHERE guild_id = {interaction.guild.id}")
         result = cursor.fetchone()
         view = Confirm(interaction)
         await interaction.response.send_message(f'{question} Are you sure you want to set {channel.mention} as the bump channel**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
            if result is None:
                link = await interaction.channel.create_invite(max_age = 0)
                link = str(link)
                sql = ("INSERT INTO bump(guild_id, channel_id, invite_url) VALUES(?,?,?)")
                val = (interaction.guild.id, channel.id, link)
                await interaction.edit_original_message(content=f"{correct} Bump channel has been set**!**")
            elif result is not None:
                sql = ("UPDATE bump SET channel_id = ? WHERE guild_id = ?")
                val = (channel.id,  interaction.guild.id)
                await interaction.edit_original_message(content=f"{correct} Bump channel has been updated**!**")
         elif view.value is False:
            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
         elif view.timeout:
            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**") 
         cursor.execute(sql, val)
         db.commit()
         cursor.close()
         db.close()
       except Exception as e:
        print(e)

    @group.command(name="description", description="Settings for the bump description!") # we use the declared group to make a command.
    @app_commands.describe(description = 'The description, which describes your server!')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def description(self, interaction: discord.Interaction, description : app_commands.Range[str, None, 1024]) -> None:
       try:
         #Method to check if the module is disabled!
         check = await modulecheck(interaction, self.module)
         if check is False:
             return
         #Advertise Description Code
         db = sqlite3.connect('Database/bump.db')
         cursor = db.cursor()
         cursor.execute(f"SELECT description FROM bump WHERE guild_id = {interaction.guild.id}")
         result = cursor.fetchone()
         view = Confirm(interaction)
         await interaction.response.send_message(f'{question} Are you sure you want to set this as the bump description**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
            if result is None:
                sql = ("INSERT INTO bump(guild_id, description) VALUES(?,?)")
                val = (interaction.guild.id, description)
                cursor.execute(sql, val)
                await interaction.edit_original_message(content=f"{correct} Bump description has been set**!**")
            elif result is not None:
                sql = ("UPDATE bump SET description = ? WHERE guild_id = ?")
                val = (description,  interaction.guild.id)
                cursor.execute(sql, val)
                await interaction.edit_original_message(content=f"{correct} Bump description has been updated**!**")
         elif view.value is False:
            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
         elif view.timeout:
            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**") 
         db.commit()
         cursor.close()
         db.close()
       except Exception as e:
        print(e)

    @group.command(name="tags", description="Settings for the bump tags!") # we use the declared group to make a command.
    @app_commands.describe(choices = 'Whether, you wish to add or remove a tag!', tag = "The tag you wish to add or remove!")
    @app_commands.choices(choices = [Choice(name="Add", value='add'), Choice(name="Remove", value="remove")], tag = [Choice(name="Community", value='community'), Choice(name="Anime", value='anime'), Choice(name="Music", value='music'), Choice(name="Technology", value='technology'), Choice(name="Gaming", value='gaming'), Choice(name="Education", value='education'), Choice(name="Entertainment", value='entertainment'), Choice(name="Advertisement", value='advertisement'), Choice(name="Social", value='social')])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def tags(self, interaction: discord.Interaction, choices : str, tag : str) -> None:
        try:
            if choices == 'add':
                self.cursor.execute(f"SELECT {tag} FROM tags WHERE guild_id = {interaction.guild.id}")
                tags = self.cursor.fetchone()
                if tags is None:
                    view = Confirm(interaction)
                    await interaction.response.send_message(f"{question} Do you want to add the `{tag.capitalize()}` tag**?**", ephemeral=True, view=view)
                    await view.wait()
                    if view.value is True:
                        self.cursor.execute(f"INSERT INTO tags(guild_id, {tag}) VALUES({interaction.guild.id}, 1)")
                        await interaction.edit_original_message(content=f"{correct} The tag `{tag.capitalize()}` has been added**!**")
                    elif view.value is False:
                        await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
                    elif view.timeout:
                        await interaction.edit_original_message(content=f"{wrong} Button timed out**!**") 
                elif tags is not None:
                    if tags[0] == 1:
                        return await interaction.response.send_message(f"{wrong} You have already added the `{tag.capitalize()}` tag**!**", ephemeral=True)
                    else:
                        view = Confirm(interaction)
                        await interaction.response.send_message(f"{question} Do you want to add the `{tag.capitalize()}` tag**?**", ephemeral=True, view=view)
                        await view.wait()
                        if view.value is True:
                            self.cursor.execute(f"UPDATE tags SET {tag} = 1 WHERE guild_id = {interaction.guild.id}")
                            await interaction.edit_original_message(content=f"{correct} The tag `{tag.capitalize()}` has been added**!**")
                        elif view.value is False:
                            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
                        elif view.timeout:
                            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**")                         
            elif choices == 'remove':
                self.cursor.execute(f"SELECT {tag} FROM tags WHERE guild_id = {interaction.guild.id}")
                tags = self.cursor.fetchone()
                if tags is None:
                    return await interaction.response.send_message(f"{wrong} The tag `{tag.capitalize()}` has not been added yet**!**", ephemeral=True)
                elif tags is not None:
                    if tags[0] == 1:
                        view = Confirm(interaction)
                        await interaction.response.send_message(f"{question} Do you want to remove the `{tag.capitalize()}` tag**?**", ephemeral=True, view=view)
                        await view.wait()
                        if view.value is True:
                            self.cursor.execute(f"UPDATE tags SET {tag} = NULL WHERE guild_id = {interaction.guild.id}")
                            await interaction.edit_original_message(content=f"{correct} The tag `{tag.capitalize()}` has been removed**!**")
                        elif view.value is False:
                            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
                        elif view.timeout:
                            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**")    
            self.db.commit()
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
     try:
      self.cursor.execute(f"DELETE FROM bump WHERE guild_id = {guild.id}")
      self.db.commit()
     except Exception as e:
      print(e)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
     try:
      self.cursor.execute(f"SELECT channel_id FROM bump WHERE guild_id = {channel.guild.id}")
      result = self.cursor.fetchone() 
      try:
        result = result[0]
      except:
          pass
      if channel.id == result:
       self.cursor.execute(f"DELETE  FROM bump WHERE guild_id = {channel.guild.id}")
       self.db.commit()
      else:
       pass
     except Exception as e:
      pass

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(Bump(bot))