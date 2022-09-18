#Importing the necessary packages
import discord
from discord import Permissions, app_commands
from discord.app_commands import Choice, describe
from discord.ext import commands
import sqlite3
import datetime
from utils.confirm import *
from utils.emojis import *
from utils.module import *

class Logs(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.module = "loggingsSys"
        self.db = sqlite3.connect('Database/logs.db')
        self.cursor = self.db.cursor()      

    group = app_commands.Group(name="logging", description="Settings for the loggings in your server!", guild_only=True)

    @group.command(name = "channel", description = "Set loggings to a specific channel!")
    @app_commands.describe(channel = "The channel, where the loggings will be sent!")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def channel(self, interaction : discord.Interaction, channel : discord.TextChannel) -> None:
       try:
        #Method to check if the module is disabled!
        check = await modulecheck(interaction, self.module)
        if check is False:
            return
        #Logging Channel Code
        view = Confirm(interaction)
        self.cursor.execute(f"SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}")
        result = self.cursor.fetchone()
        await interaction.response.send_message(f'{question} Are you sure you want to set {channel.mention} as the logging channel**?**', view=view, ephemeral=True)
        await view.wait()
        if view.value is True:
            if result is None:
                sql = ("INSERT INTO logs(guild_id, channel_id) VALUES(?,?)")
                val = (interaction.guild.id, channel.id)
                await interaction.edit_original_message(content=f"{correct} Logging channel has been set**!**")
            elif result is not None:
                sql = ("UPDATE logs SET channel_id = ? WHERE guild_id = ?")
                val = (channel.id, interaction.guild.id)
                await interaction.edit_original_message(content=f"{correct} Logging channel has been updated**!**")
        elif view.value is False:
            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**")                         
        elif view.timeout:
            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**") 
        self.cursor.execute(sql, val)
        self.db.commit()
       except Exception as e:
        print(e)

    #Channel Logs
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel) -> None:
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channels_id  FROM logs WHERE guild_id = {channel.guild.id}")
        result = cursor.fetchone()
        if not result:
            return
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            user = entry.user
        if isinstance(channel, discord.TextChannel):
            channeltype = "Text Channel"
            icon = "https://images-ext-1.discordapp.net/external/1bPCLoLb-UrGQaABUtLpGom0fNLc0XGSsI5r6-TSBbk/https/cdn.discordapp.com/emojis/957238807302914068.png"
        if isinstance(channel, discord.StageChannel):
            channeltype = "Stage Channel"
            icon = "https://images-ext-2.discordapp.net/external/lufLlyg2dwsIIk_8zmoei5nk3qdyGBC-O5Y2lU9ubRw/https/cdn.discordapp.com/emojis/959024676712095754.png"
        if isinstance(channel, discord.VoiceChannel):
            channeltype = "Voice Channel"
            icon = "https://images-ext-1.discordapp.net/external/HQ3NBLdf4-0-1lpH4FST51FSUDBHv8ckKEV4T7MJPSQ/https/cdn.discordapp.com/emojis/959023978108825600.png"
        if isinstance(channel, discord.CategoryChannel):  
            channeltype = "Category Channel"
            icon = "https://images-ext-2.discordapp.net/external/QsaxWeCmef_gXc5PpwyLmPtsVDmOPovmReeZzt062pM/https/cdn.discordapp.com/emojis/959024327121072128.png"                                  
        embed = discord.Embed(
            description=f"**Channel:** `{channel.name}`\n**ID:** `{channel.id}`\n"
            f"**Mention:** {channel.mention}\n**Created by:** `{user}`",
            color=self.green,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(
            name=f"{channeltype} Created",
            icon_url=channel.guild.icon.url,
        )
        embed.set_footer(
            text = channeltype,
            icon_url = icon
        )
        c = self.bot.get_channel(result[0])
        await c.send(embed=embed)
     except Exception as e:
         pass
        
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel) -> None:
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channels_id  FROM logs WHERE guild_id = {channel.guild.id}")
        result = cursor.fetchone()
        if not result:
            return
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            user = entry.user
        if isinstance(channel, discord.TextChannel):
            channeltype = "Text Channel"
            icon = "https://images-ext-1.discordapp.net/external/1bPCLoLb-UrGQaABUtLpGom0fNLc0XGSsI5r6-TSBbk/https/cdn.discordapp.com/emojis/957238807302914068.png"
        if isinstance(channel, discord.StageChannel):
            channeltype = "Stage Channel"
            icon = "https://images-ext-2.discordapp.net/external/lufLlyg2dwsIIk_8zmoei5nk3qdyGBC-O5Y2lU9ubRw/https/cdn.discordapp.com/emojis/959024676712095754.png"
        if isinstance(channel, discord.VoiceChannel):
            channeltype = "Voice Channel"
            icon = "https://images-ext-1.discordapp.net/external/HQ3NBLdf4-0-1lpH4FST51FSUDBHv8ckKEV4T7MJPSQ/https/cdn.discordapp.com/emojis/959023978108825600.png"
        if isinstance(channel, discord.CategoryChannel):  
            channeltype = "Category Channel"
            icon = "https://images-ext-2.discordapp.net/external/QsaxWeCmef_gXc5PpwyLmPtsVDmOPovmReeZzt062pM/https/cdn.discordapp.com/emojis/959024327121072128.png"                                  
        embed = discord.Embed(
            description=f"**Channel:** `{channel.name}`\n**ID:** `{channel.id}`\n"
            f"**Deleted by:** `{user}`",
            color=self.red,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(
            name=f"{channeltype} Deleted",
            icon_url=channel.guild.icon.url,
        )
        embed.set_footer(
            text = channeltype,
            icon_url = icon
        )
        result = result[0]
        c = self.bot.get_channel(result)
        await c.send(embed=embed)
     except Exception as e:
         pass

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after) -> None:
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT channels_id  FROM logs WHERE guild_id = {before.guild.id}")
        result = cursor.fetchone()
        if not result:
            return
        c = after
        if isinstance(c, discord.TextChannel):
            channeltype = "Text Channel"
            icon = "https://images-ext-1.discordapp.net/external/1bPCLoLb-UrGQaABUtLpGom0fNLc0XGSsI5r6-TSBbk/https/cdn.discordapp.com/emojis/957238807302914068.png"
        if isinstance(c, discord.StageChannel):
            channeltype = "Stage Channel"
            icon = "https://images-ext-2.discordapp.net/external/lufLlyg2dwsIIk_8zmoei5nk3qdyGBC-O5Y2lU9ubRw/https/cdn.discordapp.com/emojis/959024676712095754.png"
        if isinstance(c, discord.VoiceChannel):
            channeltype = "Voice Channel"
            icon = "https://images-ext-1.discordapp.net/external/HQ3NBLdf4-0-1lpH4FST51FSUDBHv8ckKEV4T7MJPSQ/https/cdn.discordapp.com/emojis/959023978108825600.png"
        if isinstance(c, discord.CategoryChannel):  
            channeltype = "Category Channel"
            icon = "https://images-ext-2.discordapp.net/external/QsaxWeCmef_gXc5PpwyLmPtsVDmOPovmReeZzt062pM/https/cdn.discordapp.com/emojis/959024327121072128.png" 
        async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update):
            user = entry.user
        channel = self.bot.get_channel(result[0])
        if before.name != after.name:
            embed = discord.Embed(
                description=f"**Channel:** {after.mention}\n**ID:** `{after.id}`\n"
                f"**Old Name:** `{before.name}`\n"
                f"**New Name:** `{after.name}`\n**Edited by:** `{user}`",
                colour=self.yellow,
                timestamp=discord.utils.utcnow(),
            )
            embed.set_author(name=f"{channeltype} Updated", icon_url=after.guild.icon.url)
            embed.set_footer(text=f"{channeltype}", icon_url=icon)
            await channel.send(embed=embed)
        elif before.category != after.category:
            embed = discord.Embed(
                description=f"**Channel:** {after.mention}\n**ID:** `{after.id}`\n"
                f"**Old Category:** `{before.category}`\n"
                f"**New Category:** `{after.category}`\n**Edited by:** `{user}`",
                colour=self.yellow,
                timestamp=discord.utils.utcnow(),
            )
            embed.set_author(name=f"{channeltype} Updated", icon_url=after.guild.icon.url)
            embed.set_footer(text=f"{channeltype}", icon_url=icon)
            await channel.send(embed=embed)
        if isinstance(before, discord.TextChannel):
            if before.topic != after.topic:
                embed = discord.Embed(
                    description=f"**Channel:** {after.mention}\n**ID:** `{after.id}`\n"
                    f"**Old Topic:** `{before.topic}`\n"
                    f"**New Topic:** `{after.topic}`\n**Edited by:** `{user}`",
                    colour=self.yellow,
                    timestamp=discord.utils.utcnow(),
                )
                embed.set_author(name=f"{channeltype} Updated", icon_url=after.guild.icon.url)
                embed.set_footer(text=f"{channeltype}", icon_url= "https://images-ext-1.discordapp.net/external/1bPCLoLb-UrGQaABUtLpGom0fNLc0XGSsI5r6-TSBbk/https/cdn.discordapp.com/emojis/957238807302914068.png")
                await channel.send(embed=embed)
        if isinstance(before, discord.TextChannel):
            if before.slowmode_delay != after.slowmode_delay:
                embed = discord.Embed(
                    description=f"**Channel:** {after.mention}\n**ID:** `{after.id}`\n"
                    f"**Old Slowmode:** `{before.slowmode_delay}`\n"
                    f"**New Slowmode:** `{after.slowmode_delay}`\n**Edited by:** `{user}`",
                    colour=self.yellow,
                    timestamp=discord.utils.utcnow(),
                )
                embed.set_author(name=f"{channeltype} Updated", icon_url=after.guild.icon.url)
                embed.set_footer(text=f"{channeltype}", icon_url= icon)
                await channel.send(embed=embed)
        if isinstance(before, discord.VoiceChannel):
            if before.user_limit != after.user_limit:
                embed = discord.Embed(
                    description=f"**Channel:** {after.mention}\n**ID:** `{after.id}`\n"
                    f"**Old User Limit:** `{before.user_limit}`\n"
                    f"**New User Limit:** `{after.user_limit}`\n**Edited by:** `{user}`",
                    colour=self.yellow,
                    timestamp=discord.utils.utcnow(),
                )
                embed.set_author(name=f"{channeltype} Updated", icon_url=after.guild.icon.url)
                embed.set_footer(text=f"{channeltype}", icon_url= icon)
                await channel.send(embed=embed)
        elif before.changed_roles != after.changed_roles:
            old_overwrites = (
                str(
                    [
                        r.mention
                        for r in before.changed_roles
                        if r != after.guild.default_role
                    ]
                )
                .replace("'", "")
                .replace("[", "")
                .replace("]", "")
            )
            new_overwrites = (
                str(
                    [
                        r.mention
                        for r in after.changed_roles
                        if r != after.guild.default_role
                    ]
                )
                .replace("'", "")
                .replace("[", "")
                .replace("]", "")
            )
            embed = discord.Embed(
                description=f"**Channel:** {after.mention}\n**ID:** `{after.id}`\n"
                f"**Old Role Overwrites:** {old_overwrites}\n"
                f"**New Role Overwrites:** {new_overwrites}\n**Edited by:** `{user}`",
                colour=self.yellow,
                timestamp=discord.utils.utcnow(),
            )
            embed.set_author(name=f"{channeltype} Updated", icon_url=after.guild.icon.url)
            embed.set_footer(text=f"{channeltype}", icon_url= icon)
            await channel.send(embed=embed)
     except Exception as e:
         pass

    #Server Logs
    @commands.Cog.listener()
    async def on_guild_update(self, before, after) -> None:
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT guilds_id  FROM logs WHERE guild_id = {before.id}")
        result = cursor.fetchone()
        if not result:
            return
        async for entry in before.audit_logs(limit=1, action=discord.AuditLogAction.guild_update):
            b = entry        
        c = self.bot.get_channel(result[0])
        if before.name != after.name:
            embed = discord.Embed(
                description=f"**Author:** {b.user.mention}\n"
                f"**Before:**: `{before.name}`\n"
                f"**After:**: `{after.name}`",
                color=self.yellow,
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(icon_url=UPDATED_MESSAGE, text=b.user)
            embed.set_author(name="Server Name Updated",icon_url=after.icon.url)
            await c.send(embed=embed)
        elif before.afk_channel != after.afk_channel:
            embed = discord.Embed(
                description=f"**Author:** {b.user.mention}\n"
                f"**Before:**: {before.afk_channel.mention}\n"
                f"**After:**: {after.afk_channel.mention}",
                color=self.yellow,
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(icon_url=UPDATED_MESSAGE, text=b.user)
            embed.set_author(name="Server Afk Channel Updated",icon_url=after.icon.url)
            await c.send(embed=embed)
        elif before.icon != after.icon:
            embed = discord.Embed(
                description=f"**Author:** {b.user.mention}\n"
                f"**Before:**: [I forgot what it was!](https://www.youtube.com/watch?v=iik25wqIuFo)\n"
                f"**After:**: [Guild icon]({after.icon.url})",
                color=self.yellow,
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(icon_url=UPDATED_MESSAGE, text=b.user)
            embed.set_author(name="Server Icon Updated",icon_url=after.icon.url)
            await c.send(embed=embed)
        elif before.banner != after.banner:   
            embed = discord.Embed(
                description=f"**Author:** {b.user.mention}\n"
                f"**Before:**: [I forgot what it was!](https://www.youtube.com/watch?v=iik25wqIuFo)\n"
                f"**After:**: [Guild banner]({after.banner.url})",
                color=self.yellow,
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(icon_url=UPDATED_MESSAGE, text=b.user)
            embed.set_author(name="Server Banner Updated",icon_url=after.icon.url)
            await c.send(embed=embed)   
        elif before.system_channel != after.system_channel:  
            embed = discord.Embed(
                description=f"**Author:** {b.user.mention}\n"
                f"**Before:**: {before.system_channel}\n"
                f"**After:**: {after.system_channel})",
                color=self.yellow,
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(icon_url=UPDATED_MESSAGE, text=b.user)
            embed.set_author(name="Server System Channel Updated",icon_url=after.icon.url)
            await c.send(embed=embed)   
        elif before.rules_channel != after.rules_channel:
            embed = discord.Embed(
                description=f"**Author:** {b.user.mention}\n"
                f"**Before:**: {before.rules_channel.mention}\n"
                f"**After:**: {after.rules_channel.mention})",
                color=self.yellow,
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(icon_url=UPDATED_MESSAGE, text=b.user)
            embed.set_author(name="Server Rules Channel Updated",icon_url=after.icon.url)
            await c.send(embed=embed)   
        elif before.public_updates_channel != after.public_updates_channel:    
            embed = discord.Embed(
                description=f"**Author:** {b.user.mention}\n"
                f"**Before:**: {before.public_updates_channel.mention}\n"
                f"**After:**: {after.public_updates_channel.mention})",
                color=self.yellow,
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(icon_url=UPDATED_MESSAGE, text=b.user)
            embed.set_author(name="Server Public Updates Channel Updated",icon_url=after.icon.url)
            await c.send(embed=embed)    
     except Exception as e:
         print(e)

    #Message update Logs
    @commands.Cog.listener()
    async def on_message_delete(self, message) -> None:
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT messages_id FROM logs WHERE guild_id = {message.guild.id}")
        result = cursor.fetchone()
        if not result:
            return
        if message.content == "":
            content = ""
        elif message.content.startswith("```"):
            content = f"**__Message Content__**\n{message.clean_content}"
        else:
            content = f"**__Message Content__**\n{message.clean_content}"

        if len(message.attachments):
            attachment_list = "\n".join(
                [f"[**`{x.filename}`**]({x.url})" for x in message.attachments]
            )
            attachments = f"**__Attachment{'' if len(message.attachments) == 1 else 's'}__**\n {attachment_list}"
            if message.content != "":
                content = content
        else:
            attachments = ""
        embed = discord.Embed(
            description=f"**Author:**  {message.author.mention}, **ID:** `{message.author.id}`\n"
            f"**Channel:** {message.channel.mention} **ID:** `{message.channel.id}`\n"
            f"{content}"
            f"{attachments}",
            color=self.red,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(
            name="Message Deleted",
            icon_url=message.guild.icon.url,
        )
        embed.set_footer(text=f"Message/Attachments" , icon_url=DELETED_MESSAGE)
        c = self.bot.get_channel(result[0])
        await c.send(embed=embed)
     except Exception as e:
         pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after) -> None:
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT messages_id FROM logs WHERE guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if not result:
            return
        if before.content == after.content:
            return 
        jump_url = f"**[Jump to message](https://discord.com/channels/{after.guild.id}/{after.channel.id}/{after.id})**"
        embed = discord.Embed(
            description=f"**Author:**  {after.author.mention} **ID:** `{after.author.id}`\n"
            f"**Channel:** {after.channel.mention} **ID:** `{after.channel.id}`\n",
            color=self.yellow,
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(
            name="__**Old Message Content**__", value=before.content, inline=False
        )
        embed.add_field(
            name="__**New Message Content**__", value=after.content, inline=False
        )
        embed.add_field(name="\u200b", value=f"{jump_url}")
        embed.set_author(name="Message Edited",icon_url=after.guild.icon.url)
        embed.set_footer(text=f"Message Edits", icon_url=UPDATED_MESSAGE)            
        c = self.bot.get_channel(result[0])
        await c.send(embed=embed)
     except Exception as e:
         pass

    #Moderations Logs
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT mods_id FROM logs WHERE guild_id = {guild.id}")
        result = cursor.fetchone()
        if not result:
            return
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            b = entry
        embed = discord.Embed(timestamp=discord.utils.utcnow(),color=self.blue, description=f"**User:** `{user.name}`\n**ID:** `{user.id}`\n**Moderator:** {b.user.mention}")
        embed.set_author(icon_url=guild.icon.url, name=f"Member Banned")
        embed.set_footer(icon_url=user.avatar.url, text=user.name)
        c = self.bot.get_channel(result[0])
        await c.send(embed=embed)
     except Exception as e:
         pass
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT mods_id FROM logs WHERE guild_id = {guild.id}")
        result = cursor.fetchone()
        if not result:
            return
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
            b = entry
        embed = discord.Embed(timestamp=discord.utils.utcnow(),color=self.blue, description=f"**User:** `{user.name}`\n**ID:** `{user.id}`\n**Moderator:** {b.user.mention}")
        embed.set_author(icon_url=guild.icon.url, name=f"Member Unbanned")
        embed.set_footer(icon_url=user.avatar.url, text=user.name)
        c = self.bot.get_channel(result[0])
        await c.send(embed=embed)
     except Exception as e:
         pass

    #Members Logs
    @commands.Cog.listener()
    async def on_member_join(self, member):
     try:
        self.cursor.execute(f"SELECT members_id FROM logs WHERE guild_id = {member.guild.id}")
        result = self.cursor.fetchone()
        if not result:
            return
        user_joined = round(datetime.datetime.now().timestamp()) 
        user_age = round(member.created_at.timestamp())
        embed = discord.Embed(timestamp=discord.utils.utcnow(), color=self.green)
        embed.set_author(icon_url=member.guild.icon.url, name=f"Member Joined")
        embed.set_footer(icon_url=member.avatar.url, text=member.name)
        channel = result[0]
        await channel.send(embed=embed)
     except Exception as e:
         pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT members_id FROM logs WHERE guild_id = {member.guild.id}")
        result = cursor.fetchone()
        if not result:
            return
        user_left = round(datetime.datetime.now().timestamp()) 
        user_joined = round(member.joined_at.timestamp())
        embed = discord.Embed(timestamp=discord.utils.utcnow(), color=self.red, description=f"**User:** `{member.name}`\n**ID:** `{member.id}`\n**Joined at:** <t:{user_joined}:D> (<t:{user_joined}:R>)\n**Left at:** <t:{user_left}:D> (<t:{user_left}:R>)")
        embed.set_author(icon_url=member.guild.icon.url, name=f"Member Left")
        embed.set_footer(icon_url=member.avatar.url, text=member.name)
        c = self.bot.get_channel(result[0])
        await c.send(embed=embed)
     except Exception as e:
         pass

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT members_id FROM logs WHERE guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if not result:
            return
        c = self.bot.get_channel(result[0])
        if before.display_name != after.display_name:
            embed = discord.Embed(timestamp=discord.utils.utcnow(),color=self.yellow, 
            description=f"**User:** {after.mention}\n**ID:** `{after.id}`\n"
                f"**Old Nickname:** `{before.display_name}`\n"
                f"**New Nickname:** `{after.display_name}`")
            embed.set_author(icon_url=after.guild.icon.url, name = f"Nickname Update") 
            embed.set_footer(icon_url=after.avatar.url, text= after.name)
            c = self.bot.get_channel(result[0])
            await c.send(embed=embed) 
        elif before.roles != after.roles:
            if "@everyone" not in [x.name for x in before.roles]:
                return
            embed = discord.Embed(
                description=f"**User:** {after.mention}\n**ID:** `{after.id}`\n"
                f"**Old Roles:** {', '.join([r.mention for r in before.roles if r != after.guild.default_role])}\n"
                f"**New Roles:** {', '.join([r.mention for r in after.roles if r != after.guild.default_role])}\n",
                colour=self.yellow,
                timestamp=discord.utils.utcnow(),
            )
            embed.set_author(icon_url=after.guild.icon.url, name ="Member Roles Update")
            embed.set_footer(icon_url=after.avatar.url, text = after.name)
            await c.send(embed=embed) 
     except Exception as e:
         pass

    #Role Logs
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT roles_id FROM logs WHERE guild_id = {role.guild.id}")
        result = cursor.fetchone()
        if not result:
            return
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
            b = entry
        embed = discord.Embed(color=self.green, timestamp=discord.utils.utcnow(), description = f"**Role:** `{role.name}`\n**ID:** `{role.id}`\n**Mention:** {role.mention}\n**Created by:** `{b.user}`")
        embed.set_author(icon_url=role.guild.icon.url, name = f"Role Created")
        embed.set_footer(icon_url=b.user.avatar.url, text=b.user)         
        c = self.bot.get_channel(result[0])
        await c.send(embed=embed)
     except Exception as e:
         pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT roles_id FROM logs WHERE guild_id = {role.guild.id}")
        result = cursor.fetchone()
        if not result:
            return
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            b = entry
        embed = discord.Embed(color=self.red, timestamp=discord.utils.utcnow(), description = f"**Role:** `{role.name}`\n**ID:** `{role.id}`\n**Mention:** {role.mention}\n**Deleted by:** `{b.user}`")
        embed.set_author(icon_url=role.guild.icon.url, name = f"Role Deleted")
        embed.set_footer(icon_url=b.user.avatar.url, text=b.user)         
        c = self.bot.get_channel(result[0])
        await c.send(embed=embed)
     except Exception as e:
         pass

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT roles_id FROM logs WHERE guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if not result:
            return
        async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update):
            b = entry
        if before.colour != after.colour:
            embed = discord.Embed(color=self.yellow, timestamp=discord.utils.utcnow(),description=f'**Mention:** {after.mention}\n**Before:** `{before.colour}`\n**After:** `{after.colour}`\n**Updated by:** {b.user.mention}') 
            embed.set_author(icon_url=before.guild.icon.url, name = f"Role Colour Updated")
            embed.set_footer(icon_url=b.user.avatar.url, text=b.user)      
            c = self.bot.get_channel(result[0])
            await c.send(embed=embed) 
        elif before.permissions != after.permissions:
            embed = discord.Embed(color=self.yellow, timestamp=discord.utils.utcnow())
            diff = list(set(after.permissions).difference(set(before.permissions)))
            for p in diff:
                embed.add_field(inline=False, name = "\u200b", value = f"• {p[0].capitalize()} set to ```{p[1]}```")
            embed.set_author(icon_url=before.guild.icon.url, name = f"Role Permissions Updated")
            embed.set_footer(icon_url=b.user.avatar.url, text=b.user)   
            c = self.bot.get_channel(result[0])
            await c.send(embed=embed)
        elif before.name != after.name:
            embed = discord.Embed(color=self.yellow, timestamp=discord.utils.utcnow(),description=f'**Mention:** {after.mention}\n**Updated by:** {b.user.mention}') 
            embed.set_author(icon_url=before.guild.icon.url, name = f"Role Name Updated")
            embed.set_footer(icon_url=b.user.avatar.url, text=b.user)      
            c = self.bot.get_channel(result[0])
            await c.send(embed=embed)
        elif before.mentionable != after.mentionable:   
            embed = discord.Embed(color=self.yellow, timestamp=discord.utils.utcnow(),description=f'**Mention:** {after.mention}\n**Before:** `{before.mentionable}`\n**After:** `{after.mentionable}`\n**Updated by:** {b.user.mention}') 
            embed.set_author(icon_url=before.guild.icon.url, name = f"Role Colour Updated")
            embed.set_footer(icon_url=b.user.avatar.url, text=b.user)      
            c = self.bot.get_channel(result[0])
            await c.send(embed=embed)             
     except Exception as e:
         pass

    #Voice logs
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
     try:
        db = sqlite3.connect('Database/logs.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT voice_id FROM logs WHERE guild_id = {member.guild.id}")
        result = cursor.fetchone()
        if not result:
            return        
        c = self.bot.get_channel(result[0])    
        if not before.channel and after.channel:
            embed = discord.Embed(
                description=f"**User:** {member.mention}\n**ID:** `{member.id}`\n**Channel:** `{after.channel.name}`\n**ID:** `{after.channel.id}`",
                colour=self.yellow,
                timestamp=discord.utils.utcnow(),
            )
            embed.set_author(name=f"User Joined Voice Channel Update", icon_url=member.guild.icon.url)
            embed.set_footer(text=member.name, icon_url=member.avatar.url)
            await c.send(embed=embed)    
        elif before.channel and not after.channel:
            embed = discord.Embed(
                description=f"**User:** {member.mention}\n**ID:** `{member.id}`\n**Channel:** `{before.channel.name}`\n**ID:** `{before.channel.id}`",
                colour=self.yellow,
                timestamp=discord.utils.utcnow(),
            )
            embed.set_author(name=f"User Left Voice Channel Update", icon_url=member.guild.icon.url)
            embed.set_footer(text=member.name, icon_url=member.avatar.url)
            await c.send(embed=embed)              
        elif before.channel and after.channel:
            if before.channel.id != after.channel.id:
                embed = discord.Embed(
                    description=f"**User:** {member.mention}\n**ID:** `{member.id}`\n"
                    f"**Old Channel:** `{before.channel.name}`\n**ID:** `{before.channel.id}`\n"
                    f"**New Channel:** `{after.channel.name}`\n**ID:** `{after.channel.id}`\n",
                    colour=self.yellow,
                    timestamp=discord.utils.utcnow(),
                )
                embed.set_author(name=f"User Switched Voice Channels Update", icon_url=member.guild.icon.url)
                embed.set_footer(text=member.name, icon_url=member.avatar.url)
                await c.send(embed=embed)        
     except Exception as e:
        print(e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
     try:
      db = sqlite3.connect('Database/logs.db')
      cursor = db.cursor()
      cursor.execute(f"DELETE FROM logs WHERE guild_id = {guild.id}")
      cursor.close()
      db.close()
     except Exception as e:
      pass

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(Logs(bot))