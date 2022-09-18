#Importing the necessary packages
from collections import Counter
import re
import typing
import discord
from discord import app_commands
from discord.app_commands import Choice, describe
from discord.ext import commands
from utils.confirm import *
from utils.emojis import *
from utils.module import *

class Moderation(commands.Cog):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        self.module = "modSys"

    async def do_removal(self, option : str, interaction : discord.Interaction, limit: int, predicate_given: typing.Callable, *, before: int = None, after: int = None):
        if before is None:
            before = interaction.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        def predicate(message: discord.Message):
            # Don't delete pinned message in any way
            return not message.pinned and predicate_given(message)

        try:
            deleted = await interaction.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden as e:
            return await interaction.edit_original_message(content=f'{wrong} I do not have the `manage_messages` permissions**!**', view=None)
        except discord.HTTPException as e:
            return await interaction.edit_original_message(content=f'{wrong} Error: {e} (try a smaller search?)**!**', view=None)

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'**{name}**: {count}' for name, count in spammers)

        to_send = '\n'.join(messages)
        await interaction.edit_original_message(content=f'{correct} Successfully removed `{deleted}` {option}**!**')

    @app_commands.command(name = 'kick', description = 'Kick a user from your server!')
    @app_commands.describe(user = 'The user you wish to kick out!', reason = "The reason why you are kicking the user!")
    @app_commands.choices(dm = [
        Choice(name = "Yes", value = "true"), Choice(name = "No", value = "false")]) 
    @app_commands.checks.has_permissions(kick_members=True)  
    @app_commands.checks.bot_has_permissions(kick_members=True)
    @app_commands.guild_only()
    async def kick(self, interaction : discord.Interaction , user : discord.User, dm : str, reason : str= None) -> None:
        try:
         #Method to check if the module is disabled!
         check = await modulecheck(interaction, self.module)
         if check is False:
            return
         #Kick Code
         if reason is None: reason = "None"
         view = Confirm(interaction)
         await interaction.response.send_message(f'{question} Are you sure you want to kick `{user.name}`**?**', view=view, ephemeral=True)
         await view.wait()
         if reason is None: 
            msg = f'> You have been warned**!** In `{interaction.guild.name}`**!**'
         else:
            msg = f'> You have been warned for `{reason}`**!** In `{interaction.guild.name}`**!**'
         if view.value is True:
                if dm == "true":                   
                    try:
                        await user.send(msg)
                    except:
                        pass
                    await interaction.guild.kick(user, reason=reason) 
                    await interaction.edit_original_message(content=f"{correct} Successfully kicked `{user.name}`**!**") 
                elif dm == "false":
                    await interaction.guild.kick(user, reason=reason)
                    await interaction.edit_original_message(content=f"{correct} Successfully kicked `{user.name}`**!**")                       
         elif view.value is False:
                await interaction.edit_original_message(content=f"{wrong} Cancelled**!**", view=None) 
         elif view.timeout:
                await interaction.edit_original_message(content=f"{wrong} Button timed out**!**", view=None)         
        except Exception as e:
            pass

    @app_commands.command(name = 'ban', description = 'Ban a user from your server!')
    @app_commands.describe(user = 'The user you wish to ban!',  reason = "The reason why you are banning the user!")
    @app_commands.choices(dm = [
        Choice(name = "Yes", value = "true"), Choice(name = "No", value = "false")])
    @app_commands.checks.has_permissions(ban_members=True)  
    @app_commands.checks.bot_has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def ban(self, interaction : discord.Interaction , user : discord.User, dm : str, reason : str= None) -> None:
        try:
         #Method to check if the module is disabled!
         check = await modulecheck(interaction, self.module)
         if check is False:
            return
         #Ban Code
         if reason is None: reason = "None"
         view = Confirm(interaction)
         await interaction.response.send_message(f'{question} Are you sure you want to ban `{user.name}`**?**', view=view, ephemeral=True)
         await view.wait()
         if reason is None: 
            msg = f'> You have been banned**!** In `{interaction.guild.name}`**!**'
         else:
            msg = f'> You have been banned for `{reason}`**!** In `{interaction.guild.name}`**!**'
         if view.value is True:
                if dm == "true":                 
                    try:
                        await user.send(msg)
                    except:
                        pass
                    await interaction.edit_original_message(content=f"{correct} Successfully banned `{user.name}`**!**") 
                    await interaction.guild.ban(user, reason=reason)
                elif dm == "false":
                    await interaction.guild.ban(user, reason=reason)
                    await interaction.edit_original_message(content=f"{correct} Successfully banned `{user.name}`**!**")                      
         elif view.value is False:
                await interaction.edit_original_message(content=f"{wrong} Cancelled**!**") 
         elif view.timeout:
                await interaction.edit_original_message(content=f"{wrong} Button timed out**!**")         
        except Exception as e:
            print(e)

    @app_commands.command(name = 'purge', description = 'Delete a certain amount of a certain type of messages! Max limit is 300!')
    @app_commands.describe(amount = 'The amount of messages you wish to prune!') 
    @app_commands.checks.has_permissions(manage_messages=True)  
    @app_commands.choices(options = [
        Choice(name = "Embeds", value = "embeds"), Choice(name = "Emojis", value = "emojis"), Choice(name = "Files", value = "files"), Choice(name = "Images", value = "images"), Choice(name = "Messages", value = "messages"), Choice(name = "Reactions", value = "reactions")])
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def purge(self, interaction : discord.Interaction , options : str, amount : int = 30) -> None:
        try:
         #Method to check if the module is disabled!
         check = await modulecheck(interaction, self.module)
         if check is False:
            return
         #Purge Code
         if amount > 300:
            return await interaction.response.send_message(f'{wrong} Too many messages to search for `({amount}/300)`**!**')
         view = Confirm(interaction)
         await interaction.response.send_message(f'{question} Are you sure you want to purge `{amount}` {options}**?**', view=view, ephemeral=True)
         await view.wait()
         if view.value is True:
            if options == "embeds":
                await self.do_removal(options,interaction, amount, lambda e: len(e.embeds))
            elif options == "emojis":
                custom_emoji = re.compile(r'<:(\w+):(\d+)>')
                def predicate(m):
                    return custom_emoji.search(m.content)
                await self.do_removal(options,interaction, amount, predicate)
            elif options == "files":
                await self.do_removal(options,interaction, amount, lambda e: len(e.attachments))
            elif options == "images":
                await self.do_removal(options,interaction, amount, lambda e: len(e.embeds) or len(e.attachments))
            elif options == "messages":
                await self.do_removal(options,interaction, amount, lambda e: True)
            elif options == "reactions":
                total_reactions = 0
                async for message in interaction.channel.history(limit=amount, before=interaction.message):
                    if len(message.reactions):
                        total_reactions += sum(r.count for r in message.reactions)
                        await message.clear_reactions()
                await interaction.edit_original_message(content = f'{correct} Successfully removed `{total_reactions}` reactions**!**', view=view)
         elif view.value is False:
            await interaction.edit_original_message(content=f"{wrong} Cancelled**!**", view = None) 
         elif view.timeout:
            await interaction.edit_original_message(content=f"{wrong} Button timed out**!**", view = None)         
        except Exception as e:
            print(e)

    @app_commands.command(name = 'warn', description = 'Warn a member in your server!')
    @app_commands.describe(user ="The user you wish to warn", dm = "Do you want to warn the member in there dms!", reason = "The reason why you are warning the user!") 
    @app_commands.choices(dm = [Choice(name = "Yes", value = "true"), Choice(name = "No", value = "false")]) 
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)  
    @app_commands.guild_only()
    async def warn(self, interaction : discord.Interaction , user : discord.User, dm : str, reason : str = None) -> None:
        try:
            #Method to check if the module is disabled!
            check = await modulecheck(interaction, self.module)
            if check is False:
                return
            #Warn Code
            view = Confirm(interaction)
            if reason is None: 
                msg = f'> You have been warned**!** In `{interaction.guild.name}`**!**'
            else:
                msg = f'> You have been warned for `{reason}`**!** In `{interaction.guild.name}`**!**'
            await interaction.response.send_message(f'{question} Are you sure you want to warn `{user.name}`**?**', view=view, ephemeral=True)
            await view.wait()
            if view.value is True:
                if dm == "true":
                    try:
                        await user.send(msg)
                    except:
                        pass
                    await interaction.edit_original_message(content=f"{correct} Successfully warned `{user.name}`**!**") 
                elif dm == "false":
                    await interaction.edit_original_message(content=f"{correct} Successfully warned `{user.name}`**!**")                       
            elif view.value is False:
                await interaction.edit_original_message(content=f"{wrong} Cancelled**!**", view=None) 
            elif view.timeout:
                await interaction.edit_original_message(content=f"{wrong} Button timed out**!**", view=None)                 
        except Exception as e:
            print(e)

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))