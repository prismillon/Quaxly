from discord import app_commands
from discord.ext import commands


@app_commands.guild_only()
class Base(commands.GroupCog):
    pass
