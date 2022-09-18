#Importing the necessary packages
import re
import discord
from discord import Interaction, Permissions, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from typing import Optional
from utils.emojis import *
from utils.paginator import *
from utils.module import *

class Information(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.module = "infoSys"

    @app_commands.command(name = 'membercount', description = 'Shows the total member/bot count!')
    @app_commands.guild_only()
    async def membercount(self, interaction : discord.Interaction) -> None:
     try:
        #Method to check if the module is disabled!
        check = await modulecheck(interaction, self.module)
        if check is False:
            return
        #Membercount Code
        bots =  len([x for x in interaction.guild.members if x.bot])
        members =  len([x for x in interaction.guild.members if not x.bot])
        embed = discord.Embed(colour=interaction.user.color, description=f"{reply} {members} 👥 {bots} 🤖")
        embed.set_author(icon_url=interaction.guild.icon.url, name=f"{interaction.guild.name} | Server count")
        await interaction.response.send_message(embed=embed)
        gay = discord.Role
        gay.edit(permissions=None)
     except Exception as e:
        pass
   
    @app_commands.command(name = 'userinfo', description = 'Shows information about on user!')
    @app_commands.guild_only()
    @app_commands.describe(user = 'The user you wish to find information on!')
    async def userinfo(self, interaction : discord.Interaction, user : Optional[discord.Member] ) -> None:
     try:
        #Method to check if the module is disabled!
        check = await modulecheck(interaction, self.module)
        if check is False:
            return
        #Userinfo Code
        if user is None: user = interaction.user
        embed = discord.Embed(description=f"ID : {user.id}", colour=interaction.user.color)
        join_pos = sorted(interaction.guild.members, key=lambda member: member.joined_at).index(user) + 1
        embed.set_author(icon_url=user.display_avatar.url, name=f"{user.name} | User Information")
        creation_date = round(user.created_at.timestamp())
        embed.add_field(inline=False, name=f'{dot} Creation Date', value=f"{reply} <t:{creation_date}:D> (<t:{creation_date}:R>)")
        joined_date = round(user.joined_at.timestamp())
        embed.add_field(inline=False, name= f'{dot} Join Date', value=f"{reply} <t:{joined_date}:D> (<t:{joined_date}:R>)")
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(inline=False, name= f"{dot} Join Position", value= f"{reply} {join_pos}/{len(interaction.guild.members)}")      
        await interaction.response.send_message(embed=embed)
     except Exception as e:
        print(e)

    @app_commands.command(name = 'serverinfo', description = 'Shows information about the server!')
    @app_commands.guild_only()
    async def serverinfo(self, interaction : discord.Interaction ) -> None:
     try:
        #Method to check if the module is disabled!
        check = await modulecheck(interaction, self.module)
        if check is False:
            return
        #Serverinfo Code
        embed = embed=discord.Embed(description=interaction.guild.description, colour=interaction.user.color)
        embed.set_author(icon_url=interaction.guild.icon.url, name=f"{interaction.guild.name} | Server Information")
        embed.add_field(inline=False, name=f'{dot} Boosts', value=f"{reply} <a:Nitro_boosting_level:999689274167406612> Level `{interaction.guild.premium_tier}` (`{interaction.guild.premium_subscription_count}` boosts)")
        embed.add_field(inline=False, name=f"{dot} Owner", value=f"{reply} {crown} [{interaction.guild.owner}](https://discord.com/users/{interaction.guild.owner_id})")
        bots =  len([x for x in interaction.guild.members if x.bot])
        embed.add_field(inline=False, name=f'{dot} Members', value=f"{reply} `{interaction.guild.member_count}` (`{bots}` :robot:)")
        text = len(interaction.guild.text_channels)
        voice = len(interaction.guild.voice_channels)
        embed.add_field(inline=True,name=f"{dot} Channels", value=f"{reply} 💬 `{text}` 🔊 `{voice}`")
        roles = len(interaction.guild.roles)
        embed.add_field(inline=True, name = f"{dot} Roles", value=f"{reply} `{roles}`")
        emojis = len(interaction.guild.emojis)
        embed.add_field(inline=True, name=f"{dot} Emojis", value=f"{reply} `{emojis}`")
        creation_date = round(interaction.guild.created_at.timestamp())
        embed.add_field(inline=False, name=f'{dot} Creation Date', value=f"{reply} <t:{creation_date}:D> (<t:{creation_date}:R>)")
        embed.set_thumbnail(url=interaction.guild.icon.url)
        view = discord.ui.View()
        style = discord.ButtonStyle.gray 
        item = discord.ui.Button(style=style, label="Server Icon", url=interaction.guild.icon.url)  # Create an item to pass into the view class.
        view.add_item(item=item)
        await interaction.response.send_message(embed=embed, view=view)
     except Exception as e:
        print(e)

    @app_commands.command(name = 'avatar', description = 'Shows user avatar!')
    @app_commands.describe(user = 'The user you wish to find there avatar!')
    @app_commands.guild_only()
    async def avatar(self, interaction : discord.Interaction, user : Optional[discord.Member] ) -> None:
     try:
        #Method to check if the module is disabled!
        check = await modulecheck(interaction, self.module)
        if check is False:
            return
        #Avatar Code
        if user is None:
            user = interaction.user
        embed = discord.Embed(colour=interaction.user.color)
        embed.set_author(icon_url=user.display_avatar.url, name=f"{user.name} | Avatar")
        embed.set_image(url= user.display_avatar.with_size(1024))
        view = discord.ui.View()
        style = discord.ButtonStyle.gray 
        item = discord.ui.Button(style=style, label="User Icon", url=user.avatar.url)  # Create an item to pass into the view class.
        view.add_item(item=item)
        await interaction.response.send_message(embed=embed, view=view)
     except Exception as e:
        pass

    @app_commands.command(name = 'banner', description = 'Shows user banner!')
    @app_commands.describe(user = 'The user you wish to find there banner!')
    @app_commands.guild_only()
    async def banner(self, interaction : discord.Interaction, user : Optional[discord.Member] ) -> None:
        try:
            if user is None:
                user = interaction.user
            banner = await self.bot.fetch_user(user.id)
            if banner.banner is None:
                return await interaction.response.send_message(f"{wrong} `{user.name}` does not have a banner**!**", ephemeral=True)
            elif banner.banner is not None:
                embed = discord.Embed(colour=interaction.user.color)
                embed.set_author(icon_url=user.display_avatar.url, name=f"{user.name} | Banner")
                embed.set_image(url=banner.banner.url)
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(e)

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(Information(bot))