import discord
import config
import sql
import os

from discord import app_commands
from discord.ext import tasks, commands
from utils import lounge_data, mkc_data
from autocomplete import cmd_autocomplete
from discord.app_commands import Choice
from datetime import datetime


@tasks.loop(minutes=10)
async def api_list():
    await lounge_data.lounge_api_full()
    await mkc_data.mkc_api_full()


intents = discord.Intents.default()
intents.members = True
bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned, intents=intents)


@bot.event
async def setup_hook():
    for cmd in filter(lambda cmd: ".py" in cmd, os.listdir(f"{os.path.dirname(__file__)}/cogs")):
        await bot.load_extension(f"cogs.{cmd[:-3]}") 

@bot.event
async def on_ready():
    if not api_list.is_running():
        api_list.start()

    await bot.wait_until_ready()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers"))

@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command: app_commands.Command):
    embed = discord.Embed(color=0x47e0ff if not interaction.command_failed else 0xFF0000, title=f"/{command.name}")
    embed.set_author(name=f"{interaction.user.display_name} ({interaction.user.name})", icon_url=interaction.user.display_avatar)
    if interaction.guild_id:
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon)
    else:
        embed.set_footer(text="dms")
    embed.timestamp = datetime.now()
    if "options" in interaction.data:
        for option in interaction.data['options']:
            embed.add_field(name=option['name'], value=option['value'])
    await bot.get_channel(1065611483897147502).send(embed=embed)


@bot.event
async def on_guild_join(guild):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers"))
    members_id = [member.id async for member in guild.fetch_members(limit=None)]
    for member in sql.get_all_users_from_server(guild.id):
        if member[0] not in members_id:
            sql.delete_player_from_server(member[0], guild.id)

@bot.event
async def on_guild_remove(guild):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers"))

@bot.event
async def on_member_remove(member: discord.Member):
    sql.delete_player_from_server(member.id, member.guild.id)


@bot.tree.command()
@app_commands.guilds(discord.Object(id=1044334030176403608))
async def sync(interaction: discord.Interaction):
    """sync global command"""
    synced = await bot.tree.sync(guild=discord.Object(id=1044334030176403608))
    syncedG = await bot.tree.sync()
    await interaction.response.send_message(content=f"synced {len(syncedG)+len(synced)} commands")


@bot.tree.command()
@app_commands.autocomplete(command=cmd_autocomplete)
@app_commands.describe(command="the command to make change on")
@app_commands.guilds(discord.Object(id=1044334030176403608))
async def load(interaction: discord.Interaction, command: str):
    """load command into bot"""
    try:
        await bot.load_extension(command)
    except Exception as error:
        await interaction.response.send_message(content=error)
    else:
        await interaction.response.send_message(content=f"succesfully loaded '{command}'")


@bot.tree.command()
@app_commands.autocomplete(command=cmd_autocomplete)
@app_commands.describe(command="the command to make change on")
@app_commands.guilds(discord.Object(id=1044334030176403608))
async def unload(interaction: discord.Interaction, command: str):
    """unload command from bot"""
    try:
        await bot.reload_extension(command)
    except Exception as error:
        await interaction.response.send_message(content=error)
    else:
        await interaction.response.send_message(content=f"succesfully reloaded '{command}'")


@bot.tree.command()
@app_commands.autocomplete(command=cmd_autocomplete)
@app_commands.describe(command="the command to make change on")
@app_commands.guilds(discord.Object(id=1044334030176403608))
async def reload(interaction: discord.Interaction, command: str):
    """reload a command from the bot"""
    try:
        await bot.unload_extension(command)
    except Exception as error:
        await interaction.response.send_message(content=error)
    else:
        await interaction.response.send_message(content=f"succesfully loaded '{command}'")


bot.run(config.TOKEN)