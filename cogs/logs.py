import logging as logger
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands


class Logging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_error
        self.log = logger.getLogger("discord.app_command.error")

    @commands.Cog.listener()
    async def on_app_command_completion(
        self, interaction: discord.Interaction, command: app_commands.Command
    ):
        embed = discord.Embed(color=0x47E0FF, title=f"/{command.name}")
        if command.parent:
            embed.title = f"/{command.parent.name} {embed.title[1:]}"
        embed.set_author(
            name=f"{interaction.user.display_name} | {interaction.user.name}",
            icon_url=interaction.user.display_avatar,
        )
        if interaction.guild_id:
            embed.set_footer(
                text=interaction.guild.name or "user install",
                icon_url=interaction.guild.icon,
            )
        else:
            embed.set_footer(text="dms")
        embed.timestamp = datetime.now()
        if "options" in interaction.data:
            for option in interaction.data["options"]:
                if option["type"] == 1:
                    for option in option["options"]:
                        embed.add_field(name=option["name"], value=option["value"])
                    break
                embed.add_field(name=option["name"], value=option["value"])
        await self.bot.get_channel(1065611483897147502).send(embed=embed)

    @commands.Cog.listener()
    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        embed = discord.Embed(
            color=0xFF0000, title=f"/{interaction.command.name}", description=error
        )
        if interaction.command.parent:
            embed.title = f"/{interaction.command.parent.name} {embed.title[1:]}"
        embed.set_author(
            name=f"{interaction.user.display_name} | {interaction.user.name}",
            icon_url=interaction.user.display_avatar,
        )
        if interaction.guild_id:
            embed.set_footer(
                text=interaction.guild.name, icon_url=interaction.guild.icon
            )
        else:
            embed.set_footer(text="dms")
        embed.timestamp = datetime.now()
        if "options" in interaction.data:
            for option in interaction.data["options"]:
                if option["type"] == 1:
                    for option in option["options"]:
                        embed.add_field(name=option["name"], value=option["value"])
                    break
                embed.add_field(name=option["name"], value=option["value"])
        msg = await self.bot.get_channel(1065611483897147502).send(
            content=f"{error} <@169497208406802432>", embed=embed
        )
        self.log.error(
            "Ignoring exception in command %r", interaction.command.name, exc_info=error
        )
        await msg.edit(content="<@169497208406802432>")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        embed = discord.Embed(color=0x97F9D8, title=f"joined {guild.name}")
        embed.add_field(name="members", value=guild.member_count)
        embed.set_author(
            name=f"{guild.owner.display_name} ({guild.owner.name})",
            icon_url=guild.owner.display_avatar,
        )
        embed.set_thumbnail(url=guild.icon)
        await self.bot.get_channel(1065611483897147502).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        embed = discord.Embed(color=0xF44336, title=f"left {guild.name}")
        embed.add_field(name="members", value=guild.member_count)
        embed.set_author(
            name=f"{guild.owner.display_name} ({guild.owner.name})",
            icon_url=guild.owner.display_avatar,
        )
        embed.set_thumbnail(url=guild.icon)
        await self.bot.get_channel(1065611483897147502).send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Logging(bot))
