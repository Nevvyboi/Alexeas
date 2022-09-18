#Importing the necessary packages
from typing import List
import discord
from discord import app_commands, ui
from discord.app_commands import Choice, describe
from discord.ext import commands
import sqlite3
import datetime
from utils.confirm import *
from utils.emojis import *
from utils.module import *
from utils.paginator import *

class Tags(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.module = "tagSys"
        self.db = sqlite3.connect('Database/main.db')
        self.cursor = self.db.cursor()

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect('Database/main.db')
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS tags(guild_id INTEGER, tagn TEXT, tagc TEXT, creation TEXT, user_id INTEGER, updated TEXT)")

    @app_commands.command(name = 'tag', description = 'View a specfic tag in your server!')
    @app_commands.describe(name = 'The name of the tag you want to view!') 
    @app_commands.checks.bot_has_permissions(send_messages=True)  
    @app_commands.guild_only()
    async def tag(self, interaction : discord.Interaction , name : str) -> None: 
     try:
        #Method to check if the module is disabled!
        check = await modulecheck(interaction, self.module)
        if check is False:
            return
        #Tag Search Code
        self.cursor.execute(f"SELECT tagn FROM tags WHERE guild_id = {interaction.guild.id}")
        data = self.cursor.fetchall()
        if data is None:
            return await interaction.response.send_message(f"{wrong} No tags in this server**!**", ephemeral=True)
        else:
            data = [''.join(i) for i in data]
            if name not in data:
                return await interaction.response.send_message(f"{wrong} That tag does not exist in this server**!**", ephemeral=True)
            else:
                sql = ("SELECT tagc FROM tags WHERE tagn = ? AND guild_id = ?")
                val = (name, interaction.guild.id)  
                self.cursor.execute(sql, val)
                t = self.cursor.fetchone()
                members = interaction.guild.member_count
                guild = interaction.guild.name
                skip = '\n'
                await interaction.response.send_message(content=str(t[0]).format(skip=skip, guild=guild, members=members))
        self.db.commit()
     except Exception as e:
        print(e)                  

    @tag.autocomplete('name')
    async def tag_autocomplete(self, interaction: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:
        db = sqlite3.connect('Database/tags.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT tagn FROM tags WHERE guild_id = {interaction.guild.id}")
        data = cursor.fetchall()
        if data is None:
            return
        else:
            data = [''.join(i) for i in data]
            tags = data
        return [app_commands.Choice(name=name, value=name)for name in tags if current.lower() in name.lower()][:25]

    group = app_commands.Group(name="tags", description="Settings for the /tag command!", guild_only=True)

    @group.command(name="create", description="Create a tag in your server for the /tag command!") # we use the declared group to make a command.
    @app_commands.describe(name = 'The name of the tag you want to create!', content = 'The things you want to put in your tag!')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def create(self, interaction : discord.Interaction, name : str, content : str):
        #Method to check if the module is disabled!
        check = await modulecheck(interaction, self.module)
        if check is False:
            return
        #Tag Create Code
        self.cursor.execute(f"SELECT tagn FROM tags WHERE guild_id = {interaction.guild.id}")
        data = self.cursor.fetchall()
        time = datetime.datetime.now().timestamp()
        view = Confirm(interaction)
        if len(data) > 25:
            return await interaction.response.send_message(f"{wrong} You have reached the max amount of tags in this server!**!**", ephemeral=True)
        else:
         await interaction.response.send_message(f'{question} Are you sure you want to create a tag called `{name}`**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
          if data is None:
            sql = ("INSERT INTO tags(guild_id, tagn, tagc, creation, user_id, updated) VALUES(?,?,?,?,?,?)")
            val = (interaction.guild.id, name, content, time, interaction.user.id, time)
            await interaction.edit_original_message(content=f"{correct} Tag `{name}` has been created!")
          elif data is not None:
            try:
                data = data[0]
            except:
                pass
            if name in data:
                return await interaction.edit_original_message(content=f"{wrong} A tag with this name already exists in this server**!**")
            else:
                sql = ("INSERT INTO tags(guild_id, tagn, tagc, creation, user_id, updated) VALUES(?,?,?,?,?,?)")
                val = (interaction.guild.id, name, content, time, interaction.user.id, time)  
                await interaction.edit_original_message(content=f"{correct} Tag `{name}` has been created!")    
         elif view.value is False:
            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
         elif view.timeout:
            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**")              
        self.cursor.execute(sql, val)
        self.db.commit()

    @group.command(name="update", description="Update the content for a tag in your server!") # we use the declared group to make a command.
    @app_commands.describe(name = 'The name of the tag you want to create!', content = 'The things you want to put in your tag!')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def update(self, interaction : discord.Interaction, name : str, content : str):
     try:
        #Method to check if the module is disabled!
        check = await modulecheck(interaction, self.module)
        if check is False:
            return
        #Tag Update Code
        view = Confirm(interaction)
        time = datetime.datetime.now().timestamp()
        self.cursor.execute(f"SELECT tagn FROM tags WHERE guild_id = {interaction.guild.id}")
        data = self.cursor.fetchall()
        if data is None:
            return await interaction.response.send_message(f"{wrong} No tags in this server**!**", ephemeral=True)
        else:
         await interaction.response.send_message(f'{question} Are you sure you want to update the tag called `{name}`**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
            data = [''.join(i) for i in data]
            if name not in data:
                return await interaction.edit_original_message(content=f"{wrong} That tag does not exist in this server**!**")
            else:
                sql = ("UPDATE tags SET tagc = ?, updated = ? WHERE tagn = ? AND guild_id = ?")
                val = (content, time, name, interaction.guild.id)  
                await interaction.edit_original_message(content=f"{correct} Tag `{name}` has been updated!")       
         elif view.value is False:
            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
         elif view.timeout:
            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**")              
        self.cursor.execute(sql, val)
        self.db.commit()
     except Exception as e:
         print(e)

    @update.autocomplete('name')
    async def update_autocomplete(self, interaction: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:
        db = sqlite3.connect('Database/tags.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT tagn FROM tags WHERE guild_id = {interaction.guild.id}")
        data = cursor.fetchall()
        if data is None:
            return
        else:
            data = [''.join(i) for i in data]
            tags = data
        return [app_commands.Choice(name=name, value=name)for name in tags if current.lower() in name.lower()][:25]

    @group.command(name="delete", description="Delete a tag in your server!") # we use the declared group to make a command.
    @app_commands.describe(name = 'The name of the tag you want to delete!')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def delete(self, interaction : discord.Interaction, name : str):
        #Method to check if the module is disabled!
        check = await modulecheck(interaction, self.module)
        if check is False:
            return
        #Tag Search Code
        view = Confirm(interaction)
        self.cursor.execute(f"SELECT tagn FROM tags WHERE guild_id = {interaction.guild.id}")
        data = self.cursor.fetchall()
        if data is None:
            return await interaction.response.send_message(f"{wrong} No tags in this server**!**", ephemeral=True)
        else:
         await interaction.response.send_message(f'{question} Are you sure you want to delete the tag called `{name}`**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
            data = [''.join(i) for i in data]
            if name not in data:
                return await interaction.edit_original_message(content=f"{wrong} That tag does not exist in this server**!**")
            else:
                sql = ("DELETE FROM tags WHERE tagn = ? AND guild_id = ?")
                val = (name, interaction.guild.id)  
                await interaction.edit_original_message(content=f"{correct} Tag `{name}` has been deleted!") 
         elif view.value is False:
            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
         elif view.timeout:
            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**")                 
        self.cursor.execute(sql, val)
        self.db.commit()

    @delete.autocomplete('name')
    async def delete_autocomplete(self, interaction: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:
        db = sqlite3.connect('Database/tags.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT tagn FROM tags WHERE guild_id = {interaction.guild.id}")
        data = cursor.fetchall()
        if data is None:
            return
        else:
            data = [''.join(i) for i in data]
            tags = data
        return [app_commands.Choice(name=name, value=name)for name in tags if current.lower() in name.lower()][:25]

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
      db = sqlite3.connect('Database/tags.db')
      cursor = db.cursor()
      cursor.execute(f"DELETE FROM tags WHERE guild_id = {guild.id}")
      db.commit()
      cursor.close()
      db.close()

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(Tags(bot))