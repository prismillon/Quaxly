import discord
import sql

from utils import wait_for_chunk
from discord import app_commands

@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(player="the player you want to register")
async def register_user(ctx: discord.Interaction, player: discord.Member = None):
    """register a user in the timetrial database of the server"""

    if not ctx.guild.chunked:
        return await wait_for_chunk(ctx)

    embed = discord.Embed(color=0x47e0ff, description="")

    if not player:
        player = ctx.guild.get_member(ctx.user.id)

    embed.set_thumbnail(url=player.avatar)

    if len(sql.check_player(player.id)) == 0:
        sql.register_new_player(player.id)

    if len(sql.check_player_server(player.id, ctx.guild_id)) == 0:
        sql.register_user_in_server(player.id, ctx.guild_id)
        embed.title = "registered !"
        embed.description = f"{player.display_name} as been added to the list"
    else:
        embed.title = "already in >:("
        embed.description = f"{player.display_name} is already in the list"
    
    return await ctx.response.send_message(embed=embed)


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(player="the player you want to remove")
async def remove_user(ctx: discord.Interaction, player: discord.Member = None):
    """remove a user from the timetrial database of the server"""

    if not ctx.guild.chunked:
        return await wait_for_chunk(ctx)

    embed = discord.Embed(color=0x47e0ff, description="")

    if not player:
        player = ctx.guild.get_member(ctx.user.id)

    embed.set_thumbnail(url=player.avatar)

    if len(sql.check_player(player.id)) == 1 and len(sql.check_player_server(player.id, ctx.guild_id)) == 1:
        sql.delete_player_from_server(player.id, ctx.guild_id)
        embed.title = "removed !"
        embed.description = f"{player.display_name} as been removed from the list"
    else:
        embed.title = "not in >:("
        embed.description = f"{player.display_name} is not in the list"
    
    return await ctx.response.send_message(embed=embed)