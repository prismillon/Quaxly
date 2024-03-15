import re
import discord

from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

import utils
import sql

class ImportCSV(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(speed="the mode your list correspond to", items="is it with shroom or not")
    @app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
    async def import_csv(self, interaction: discord.Interaction, speed: Choice[str], items: Choice[str], csv: str):
        """import time from csv format"""

        if ',' not in csv:
            return await interaction.response.send_message("csv format is wrong")
        
        tracks = [list(track) for track in await sql.get_track_details('%')]
        tracks = list(map(lambda x: [x[1], x[4]], tracks))

        csv_lines = re.findall("[a-zA-Z0-9\ \-']+,\d:\d{2}\.\d{3}", csv)
        count = 0

        for line in csv_lines:
            if ',' not in line:
                continue
            track, time = line.split(',')
            matching_track = discord.utils.find(lambda x: x[1].lower() == track.strip().lower(), tracks)
            if not matching_track:
                continue
            try:
                await sql.save_time(items.value+speed.value, interaction.user.id, matching_track[0], time)
                count += 1
            except:
                pass
        
        await interaction.response.send_message(f"{count} times imported")


async def setup(bot: commands.Bot):
    await bot.add_cog(ImportCSV(bot))