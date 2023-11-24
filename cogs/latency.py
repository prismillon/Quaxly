import discord
import aiohttp

from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Latency(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def latency(self, interaction: discord.Interaction):
        """show bot latency from all the service it's using"""

        await interaction.response.defer()

        embed = discord.Embed(color=0x47e0ff, title="quaxly latency")
        embed.add_field(name="discord API", value=f"{round(self.bot.latency, 3)}s")
        async with aiohttp.ClientSession() as session:
            lounge_latency = datetime.now()
            async with session.get('https://www.mk8dx-lounge.com/api/player?discordId=169497208406802432') as response:
                if response.status == 200:
                    embed.add_field(name="lounge API", value=f"{round((datetime.now() - lounge_latency).total_seconds(), 3)}s")
                else:
                    embed.add_field(name="lounge API", value="no response")
            mkc_latency = datetime.now()
            async with session.get('https://www.mariokartcentral.com/mkc/api/registry/players/1', ssl=False) as response:
                if response.status == 200:
                    embed.add_field(name="mkc API", value=f"{round((datetime.now() - mkc_latency).total_seconds(), 3)}s")
                else:
                    embed.add_field(name="mkc API", value="no response")

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Latency(bot))
