import discord
import aiohttp
import re

from typing import List
from discord import app_commands
from discord.ext import commands


async def get_host_string(
    host: str, interaction: discord.Interaction, game: str = "mkworld"
):
    base_url = "https://lounge.mkcentral.com/api/player/details?"

    if re.match("^([0-9]{4}-){2}[0-9]{4}$", host):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}fc={host}&game={game}") as response:
                if response.status == 200:
                    json_data = await response.json()
                    if "discordId" in json_data:
                        return f"{host} (<@{json_data['discordId']}>)"

    elif (
        re.match("[0-9<@> ]+", host)
        and interaction.guild.get_member(int(re.findall("[0-9]+", host)[0])) is not None
    ):
        async with aiohttp.ClientSession() as session:
            host_id = re.findall("[0-9]+", host)[0]
            async with session.get(
                f"{base_url}discordId={host_id}&game={game}"
            ) as response:
                if response.status == 200:
                    json_data = await response.json()
                    if "discordId" in json_data and "switchFc" in json_data:
                        return f"{json_data['switchFc']} (<@{json_data['discordId']}>)"

    return host


class EditLineupButton(discord.ui.View):
    def __init__(self, embed: discord.Embed, old_view: discord.ui.View, owner: int):
        super().__init__(timeout=90)
        self.old_view = old_view
        self.embed = embed
        self.owner = owner

    @discord.ui.select(cls=discord.ui.UserSelect, min_values=1, max_values=6)
    async def edit_lineup(
        self, interaction: discord.Interaction, users: List[discord.Member]
    ):
        if interaction.user.id != self.owner:
            return await interaction.response.send_message(
                content="only the owner can use this sorry", ephemeral=True
            )
        self.embed.remove_field(0)
        self.embed.insert_field_at(
            0,
            name="lineup",
            value=" - ".join(
                user.mention
                for user in sorted(
                    users.values, key=lambda user: user.display_name.lower()
                )
            ),
            inline=False,
        )
        self.stop()
        await interaction.response.edit_message(embed=self.embed, view=self.old_view)

    async def on_timeout(self):
        await self.old_view.message.edit(view=self.old_view)


class EditModal(discord.ui.Modal, title="edit lineup"):
    def __init__(
        self, embed: discord.Embed, enemy_tag: str, tag: str, view: discord.ui.View
    ):
        super().__init__()
        self.embed = embed
        self.old_enemy_tag = enemy_tag
        self.old_tag = tag
        self.view = view

    time = discord.ui.TextInput(label="time", required=False)
    host = discord.ui.TextInput(label="host", required=False)
    enemy_tag = discord.ui.TextInput(label="enemy tag", required=False)
    tag = discord.ui.TextInput(label="tag", required=False)

    async def on_submit(self, interaction: discord.Interaction):

        if self.time.value != "":
            self.embed.remove_field(1)
            self.embed.insert_field_at(
                1,
                name="open",
                value=(
                    f"`{self.time.value}`"
                    if "<t:" not in self.time.value
                    else self.time.value
                ),
                inline=True,
            )

        if self.host.value != "":
            self.embed.remove_field(2)
            self.embed.insert_field_at(
                2,
                name="host",
                value=await get_host_string(self.host.value, interaction),
                inline=True,
            )

        if self.enemy_tag.value != "" and self.tag.value != "":
            self.embed.title = f"clan war | {self.tag.value} vs {self.enemy_tag.value}"
            self.view.tag = self.tag.value
            self.view.enemy_tag = self.enemy_tag.value
        elif self.enemy_tag.value != "":
            self.embed.title = f"clan war | {self.old_tag} vs {self.enemy_tag.value}"
            self.view.enemy_tag = self.enemy_tag.value
        elif self.tag.value != "":
            self.embed.title = f"clan war | {self.tag.value} vs {self.old_enemy_tag}"
            self.view.tag = self.tag.value
        await interaction.response.edit_message(embed=self.embed)


class EditButtons(discord.ui.View):
    def __init__(self, embed: discord.Embed, owner: int, enemy_tag: str, tag: str):
        super().__init__(timeout=7200)
        self.embed = embed
        self.owner = owner
        self.enemy_tag = enemy_tag
        self.tag = tag

    @discord.ui.button(emoji="📝", style=discord.ButtonStyle.gray)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner:
            return await interaction.response.send_message(
                content="you are not the owner of the message sorry", ephemeral=True
            )
        modal = EditModal(self.embed, self.enemy_tag, self.tag, self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(emoji="👥", style=discord.ButtonStyle.gray)
    async def players(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.owner:
            return await interaction.response.send_message(
                content="you are not the owner of the message sorry", ephemeral=True
            )
        await interaction.response.edit_message(
            view=EditLineupButton(self.embed, self, self.owner)
        )

    async def on_timeout(self):
        await self.message.edit(view=None)


class Lineup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(
        players="List of the players for this lineup (you have to tag them)",
        time="The time of the war is scheduled for. Any format",
        host="Friend code or tag the host of the war",
        enemy_tag="Name or tag of the enemy team",
        tag="Name or tag of your team",
    )
    async def lineup(
        self,
        interaction: discord.Interaction,
        players: str,
        time: str,
        host: str,
        enemy_tag: str,
        tag: str,
    ):
        """create a clan war line-up for your team"""

        if not interaction.channel.permissions_for(interaction.guild.me).send_messages:
            return await interaction.response.send_message(
                "I don't have permission to send message in this channel"
            )

        embed = (
            discord.Embed(color=0x47E0FF, title=f"clan war | {tag} vs {enemy_tag}")
            .set_thumbnail(url=interaction.guild.icon)
            .set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar,
            )
        )
        member_string = " - ".join(
            player.mention
            for player in sorted(
                list(
                    set(
                        [
                            interaction.guild.get_member(int(player))
                            for player in re.findall("[0-9]+", players)
                            if interaction.guild.get_member(int(player))
                        ]
                    )
                ),
                key=lambda user: user.display_name.lower(),
            )
        )
        host_string = await get_host_string(host, interaction)

        embed.add_field(name="lineup", value=member_string, inline=False)
        embed.add_field(
            name="open", value=f"`{time}`" if "<t:" not in time else time, inline=True
        )
        embed.add_field(name="host", value=host_string, inline=True)

        view = EditButtons(embed, interaction.user.id, enemy_tag, tag)

        await interaction.response.send_message(
            content=f"lineup war {time} vs {enemy_tag} || {member_string} ||"
        )
        view.message = await interaction.channel.send(embed=embed, view=view)
        await interaction.delete_original_response()


async def setup(bot):
    await bot.add_cog(Lineup(bot))
