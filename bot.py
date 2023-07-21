import discord
import config
import os

from discord.ext import commands


intents = discord.Intents.default()
intents.members = True
bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned, intents=intents, help_command=None)


@bot.event
async def setup_hook():
    for cmd in filter(lambda cmd: ".py" in cmd, os.listdir(f"{os.path.dirname(__file__)}/cogs")):
        await bot.load_extension(f"cogs.{cmd[:-3]}")


bot.run(config.TOKEN, root_logger=True)
