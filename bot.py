import discord
import config
import os

from discord.ext import commands


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned, intents=intents, help_command=None, activity=discord.Activity(type=discord.ActivityType.watching, name="starting..."), status=discord.Status('dnd'))


@bot.event
async def setup_hook():
    for cmd in filter(lambda cmd: not cmd.startswith("__"), os.listdir(f"{os.path.dirname(__file__)}/cogs")):
        await bot.load_extension(f"cogs.{cmd.replace('.py', '')}")


bot.run(config.TOKEN, root_logger=True)
