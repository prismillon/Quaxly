import discord

from discord import app_commands
from db import db


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(player="the player you want to register")
async def register_user(
    interaction: discord.Interaction, player: discord.Member = None
):
    """register a user in the timetrial database of the server"""

    embed = discord.Embed(color=0x47E0FF, description="")

    player = player or interaction.user

    embed.set_thumbnail(url=player.avatar)

    user = await db.Users.find_one({"discordId": player.id})

    if not user:
        await db.Users.insert_one(
            {"discordId": player.id, "servers": [{"serverId": interaction.guild_id}]}
        )

    else:
        if interaction.guild_id not in [
            server["serverId"] for server in user["servers"]
        ]:
            await db.Users.update_one(
                {"discordId": player.id},
                {"$push": {"servers": {"serverId": interaction.guild_id}}},
            )
        else:
            return await interaction.response.send_message(
                content="player is already in the list", ephemeral=True
            )

    embed.title = "registered !"
    embed.description = f"{player.display_name} has been added to the list"
    await interaction.response.send_message(embed=embed)


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(player="the player you want to remove")
async def remove_user(interaction: discord.Interaction, player: discord.Member = None):
    """remove a user from the timetrial database of the server"""

    embed = discord.Embed(color=0x47E0FF, description="")

    player = player or interaction.user

    embed.set_thumbnail(url=player.avatar)

    user = await db.Users.find_one({"discordId": player.id})

    if not user or interaction.guild_id not in [
        server["serverId"] for server in user["servers"]
    ]:
        return await interaction.response.send_message(
            content="player is not in the list", ephemeral=True
        )

    await db.Users.update_one(
        {"discordId": player.id},
        {"$pull": {"servers": {"serverId": interaction.guild_id}}},
    )
    embed.title = "removed !"
    embed.description = f"{player.display_name} has been removed from the list"
    return await interaction.response.send_message(embed=embed)


async def setup(bot):
    bot.tree.add_command(register_user)
    bot.tree.add_command(remove_user)
