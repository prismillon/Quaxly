import discord
import aiohttp
import re

from discord import app_commands
from autocomplete import name_autocomplete
from utils import lounge_data
from datetime import datetime, timedelta


@app_commands.command()
@app_commands.autocomplete(player=name_autocomplete)
@app_commands.describe(player="The player you want to check lounge name history from")
async def name_history(interaction: discord.Interaction, player: str = None):
    """lounge name history of a player"""

    embed = discord.Embed(color=0x47e0ff, title="name history")

    if not player:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.mk8dx-lounge.com/api/player?discordId="+str(interaction.user.id)) as response:
                if response.status == 200:
                    user_data = await response.json()
                    player = user_data['name']
                else:
                    return await interaction.response.send_message(content="could not found your account in the lounge", ephemeral=True)

    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.mk8dx-lounge.com/api/player/details?name="+player) as response:
            if response.status == 200:
                data = await response.json()

                next_change = round(datetime.fromisoformat(data['nameHistory'][-1]['changedOn']).timestamp() + timedelta(days=60).total_seconds())
                embed.add_field(name="next change", value=f"<t:{next_change}:f> <t:{next_change}:R>", inline=False)

                name_history_string = ""
                for change in data['nameHistory']:
                    name_history_string += f"<t:{round(datetime.fromisoformat(change['changedOn']).timestamp())}:f>: {change['name']}\n"

                embed.add_field(name="name change", value=name_history_string, inline=False)

            else:
                embed.description = "player not found"

    await interaction.response.send_message(embed=embed)


async def setup(bot):
    bot.tree.add_command(name_history)
