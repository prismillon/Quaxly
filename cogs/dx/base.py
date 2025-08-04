from discord import app_commands
from discord.ext import commands


@app_commands.guild_only()
class Base(
    commands.GroupCog, name="dx", description="Mario Kart 8 Deluxe timetrial commands"
):
    pass
