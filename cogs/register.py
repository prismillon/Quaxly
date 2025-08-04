import discord
from discord import app_commands
from discord.ext import commands

from database import get_db_session
from models import User, UserServer


@app_commands.command()
@app_commands.guild_only()
async def register(interaction: discord.Interaction):
    """Register yourself in the timetrial database of the server"""

    embed = discord.Embed(color=0x47E0FF, description="")
    player = interaction.user
    embed.set_thumbnail(url=player.avatar)

    with get_db_session() as session:
        user = session.query(User).filter(User.discord_id == player.id).first()

        if not user:
            user = User(discord_id=player.id)
            session.add(user)
            session.flush()

            user_server = UserServer(user_id=user.id, server_id=interaction.guild_id)
            session.add(user_server)
            session.commit()

        else:
            user_server = (
                session.query(UserServer)
                .filter(
                    UserServer.user_id == user.id,
                    UserServer.server_id == interaction.guild_id,
                )
                .first()
            )

            if user_server:
                return await interaction.response.send_message(
                    content="You are already registered in this server", ephemeral=True
                )

            user_server = UserServer(user_id=user.id, server_id=interaction.guild_id)
            session.add(user_server)
            session.commit()

    embed.title = "Registered!"
    embed.description = (
        f"{player.display_name} has been added to the server's time trial database"
    )
    await interaction.response.send_message(embed=embed)


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(player="the player you want to remove")
async def remove_user(interaction: discord.Interaction, player: discord.Member = None):
    """Remove a user from the timetrial database of the server"""

    embed = discord.Embed(color=0x47E0FF, description="")
    player = player or interaction.user
    embed.set_thumbnail(url=player.avatar)

    with get_db_session() as session:
        user = session.query(User).filter(User.discord_id == player.id).first()

        if not user:
            return await interaction.response.send_message(
                content="Player is not registered", ephemeral=True
            )

        user_server = (
            session.query(UserServer)
            .filter(
                UserServer.user_id == user.id,
                UserServer.server_id == interaction.guild_id,
            )
            .first()
        )

        if not user_server:
            return await interaction.response.send_message(
                content="Player is not registered in this server", ephemeral=True
            )

        session.delete(user_server)
        session.commit()

    embed.title = "Removed!"
    embed.description = (
        f"{player.display_name} has been removed from the server's time trial database"
    )
    return await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    bot.tree.add_command(register)
    bot.tree.add_command(remove_user)
