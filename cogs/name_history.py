import discord
import aiohttp
import re

from discord import app_commands
from autocomplete import name_autocomplete
from datetime import datetime, timedelta
from utils import lounge_data


@app_commands.command()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.autocomplete(player=name_autocomplete)
@app_commands.describe(player="The player you want to check lounge name history from")
async def name_history(interaction: discord.Interaction, player: str = None):
    """lounge name history of a player"""

    if not player:
        lounge_user = discord.utils.find(
            lambda player: player["discordId"] == str(interaction.user.id),
            lounge_data.data(),
        )
        if not lounge_user:
            return await interaction.response.send_message(
                content="could not found your account in the lounge", ephemeral=True
            )

    player = player or lounge_user["name"]

    await interaction.response.defer()
    embed = discord.Embed(color=0x47E0FF, title="name history")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://www.mk8dx-lounge.com/api/player/details?name=" + player
        ) as response:
            if response.status == 200:
                data = await response.json()

                next_change = round(
                    datetime.fromisoformat(
                        data["nameHistory"][0]["changedOn"]
                    ).timestamp()
                    + timedelta(days=60).total_seconds()
                )
                embed.add_field(
                    name="next change",
                    value=f"<t:{next_change}:f> <t:{next_change}:R>",
                    inline=False,
                )

                name_history_string = ""
                for change in data["nameHistory"]:
                    name_history_string += f"<t:{round(datetime.fromisoformat(change['changedOn']).timestamp())}:f>: {change['name']}\n"

                embed.add_field(
                    name="name change", value=name_history_string, inline=False
                )

            else:
                embed.description = "player not found"

    await interaction.followup.send(embed=embed)


async def setup(bot):
    bot.tree.add_command(name_history)
