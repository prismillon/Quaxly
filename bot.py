import discord
import config
import cogs
import sql

from discord import app_commands
from discord.ext import tasks
from utils import lounge_data, mkc_data


class MyClient(discord.AutoShardedClient):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        [self.tree.add_command(command) for command in cogs.commands]

    @tasks.loop(minutes=10)
    async def api_list(self):
        await lounge_data.lounge_api_full()
        await mkc_data.mkc_api_full()

bot = MyClient()


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers"))

    if not bot.api_list.is_running():
        bot.api_list.start()

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
async def sync(ctx: discord.Interaction):
    """sync global command"""
    synced = await bot.tree.sync(guild=discord.Object(id=1044334030176403608))
    syncedG = await bot.tree.sync()
    await ctx.response.send_message(content=f"synced {len(syncedG)+len(synced)} commands")


bot.run(config.TOKEN)