from discord.ext import commands
from discord import app_commands


@app_commands.guild_only()
class Base(commands.GroupCog):
    pass
