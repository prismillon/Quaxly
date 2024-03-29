import discord

from discord import app_commands

import sql

@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(player="the player you want to register")
async def register_user(interaction: discord.Interaction, player: discord.Member = None):
    """register a user in the timetrial database of the server"""

    embed = discord.Embed(color=0x47e0ff, description="")

    player = player or interaction.user

    embed.set_thumbnail(url=player.avatar)

    if len(await sql.check_player(player.id)) == 0:
        await sql.register_new_player(player.id)

    if len(await sql.check_player_server(player.id, interaction.guild_id)) == 0:
        await sql.register_user_in_server(player.id, interaction.guild_id)
        embed.title = "registered !"
        embed.description = f"{player.display_name} has been added to the list"
    else:
        embed.title = "already in >:("
        embed.description = f"{player.display_name} is already in the list"

    return await interaction.response.send_message(embed=embed)


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(player="the player you want to remove")
async def remove_user(interaction: discord.Interaction, player: discord.Member = None):
    """remove a user from the timetrial database of the server"""

    embed = discord.Embed(color=0x47e0ff, description="")

    player = player or interaction.user

    embed.set_thumbnail(url=player.avatar)

    if len(await sql.check_player(player.id)) == 1 and len(await sql.check_player_server(player.id, interaction.guild_id)) == 1:
        await sql.delete_player_from_server(player.id, interaction.guild_id)
        embed.title = "removed !"
        embed.description = f"{player.display_name} has been removed from the list"
    else:
        embed.title = "not in >:("
        embed.description = f"{player.display_name} is not in the list"

    return await interaction.response.send_message(embed=embed)


async def setup(bot):
    bot.tree.add_command(register_user)
    bot.tree.add_command(remove_user)
    