import discord

from discord import app_commands
from autocomplete import cmd_autocomplete
from discord.ext import commands


class extensions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.autocomplete(command=cmd_autocomplete)
    @app_commands.describe(command="the command to make change on")
    @app_commands.guilds(discord.Object(id=1044334030176403608))
    async def load(self, interaction: discord.Interaction, command: str):
        """load command into bot"""
        try:
            await self.bot.load_extension(command)
        except Exception as error:
            await interaction.response.send_message(content=error)
        else:
            await interaction.response.send_message(content=f"succesfully loaded '{command}'")


    @app_commands.command()
    @app_commands.autocomplete(command=cmd_autocomplete)
    @app_commands.describe(command="the command to make change on")
    @app_commands.guilds(discord.Object(id=1044334030176403608))
    async def unload(self, interaction: discord.Interaction, command: str):
        """unload command from bot"""
        try:
            await self.bot.reload_extension(command)
        except Exception as error:
            await interaction.response.send_message(content=error)
        else:
            await interaction.response.send_message(content=f"succesfully unloaded '{command}'")


    @app_commands.command()
    @app_commands.autocomplete(command=cmd_autocomplete)
    @app_commands.describe(command="the command to make change on")
    @app_commands.guilds(discord.Object(id=1044334030176403608))
    async def reload(self, interaction: discord.Interaction, command: str):
        """reload a command from the bot"""
        try:
            await self.bot.unload_extension(command)
        except Exception as error:
            await interaction.response.send_message(content=error)
        else:
            await interaction.response.send_message(content=f"succesfully reloaded '{command}'")


async def setup(bot: commands.Bot):
    await bot.add_cog(extensions(bot))
