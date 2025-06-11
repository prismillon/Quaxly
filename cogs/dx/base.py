from discord.ext import commands
from discord import app_commands


@app_commands.guild_only()
class Base(
    commands.GroupCog, name="dx", description="Mario Kart 8 Deluxe timetrial commands"
):
    pass
