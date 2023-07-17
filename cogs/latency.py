import discord
import requests

from discord.ext import commands
from discord import app_commands

class latency(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def latency(self, interaction: discord.Interaction):
        """show bot latency from all the service it's using"""

        await interaction.response.defer()

        embed = discord.Embed(color=0x47e0ff, title="quaxly latency")
        embed.add_field(name="discord API", value=f"{round(self.bot.latency, 3)}ms")
        embed.add_field(name="lounge API", value=f"{round(requests.get('https://www.mk8dx-lounge.com/api/player').elapsed.total_seconds(), 3)}ms")
        embed.add_field(name="mkc API", value=f"{round(requests.get('https://www.mariokartcentral.com/mkc/api/registry/players/1').elapsed.total_seconds(), 3)}ms")

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(latency(bot))
