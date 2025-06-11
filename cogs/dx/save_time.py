import datetime
import discord
import re

from discord import app_commands
from discord.app_commands import Choice
from .autocomplete import dx_track_autocomplete, dx_time_autocomplete
from utils import ConfirmButton
from database import get_db_session
from models import User, Track, TimeRecord, UserServer, GAME_MK8DX
from game_utils import get_track_by_name, validate_game
import utils


def time_diff(new_time, previous_time):
    """Calculate the difference between two times"""
    diff = datetime.datetime.strptime(
        previous_time, "%M:%S.%f"
    ) - datetime.datetime.strptime(new_time, "%M:%S.%f")
    return (
        f"{diff.seconds // 60}:{diff.seconds % 60:02d}.{diff.microseconds // 1000:03d}"
    )


class SaveTimeCommands:
    """Save time command for MK8DX"""

    @app_commands.command(name="save_time")
    @app_commands.guild_only()
    @app_commands.describe(
        speed="the mode you are playing in",
        items="are you using shrooms?",
        track="the track you are playing on",
        time="your time formatted like this -> 1:23.456",
    )
    @app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
    @app_commands.autocomplete(track=dx_track_autocomplete, time=dx_time_autocomplete)
    async def save_time(
        self,
        interaction: discord.Interaction,
        speed: Choice[str],
        items: Choice[str],
        track: str,
        time: app_commands.Range[str, 8, 8],
    ):
        """Save a time for MK8DX"""

        game = GAME_MK8DX
        race_type = items.value
        speed_value = int(speed.value)

        embed = discord.Embed(color=0x47E0FF, description="")
        player = interaction.user

        if not re.fullmatch("^\\d:[0-5]\\d\\.\\d{3}$", time):
            return await interaction.response.send_message(
                content=f"{time} is not a valid formatted time like this (1:23.456)",
                ephemeral=True,
            )

        with get_db_session() as session:
            track_obj = get_track_by_name(session, game, track)
            if not track_obj:
                return await interaction.response.send_message(
                    content="track not found", ephemeral=True
                )

            user = session.query(User).filter(User.discord_id == player.id).first()
            if not user:
                user = User(discord_id=player.id)
                session.add(user)
                session.flush()

                user_server = UserServer(
                    user_id=user.id, server_id=interaction.guild.id
                )
                session.add(user_server)

            user_server = (
                session.query(UserServer)
                .filter(
                    UserServer.user_id == user.id,
                    UserServer.server_id == interaction.guild.id,
                )
                .first()
            )
            if not user_server:
                user_server = UserServer(
                    user_id=user.id, server_id=interaction.guild.id
                )
                session.add(user_server)

            existing_time = (
                session.query(TimeRecord)
                .filter(
                    TimeRecord.user_id == user.id,
                    TimeRecord.track_id == track_obj.id,
                    TimeRecord.game == game,
                    TimeRecord.race_type == race_type,
                    TimeRecord.speed == speed_value,
                )
                .first()
            )

            time_ms = TimeRecord.time_to_milliseconds(time)

            embed.title = f"time saved in {speed.name} {items.name}"
            embed.description = (
                f"{player.display_name} saved ``{time}`` on **{track_obj.track_name}**"
            )
            embed.set_thumbnail(url=track_obj.track_url)

            if not existing_time:
                new_time_record = TimeRecord(
                    user_id=user.id,
                    track_id=track_obj.id,
                    game=game,
                    time=time,
                    race_type=race_type,
                    speed=speed_value,
                    time_milliseconds=time_ms,
                )
                session.add(new_time_record)
                session.commit()
                return await interaction.response.send_message(embed=embed)

            elif existing_time.time_milliseconds > time_ms:
                old_time = existing_time.time
                existing_time.time = time
                existing_time.time_milliseconds = time_ms
                existing_time.updated_at = datetime.datetime.utcnow()

                embed.description += (
                    f"\nyou improved by ``{time_diff(time, old_time)}`` !"
                )
                session.commit()
                return await interaction.response.send_message(embed=embed)

            else:
                embed.title = "conflict with previous time"
                embed.description = f"you already have ``{existing_time.time}`` on this track do you still want to make this change?"
                view = ConfirmButton()
                await interaction.response.send_message(
                    embed=embed, view=view, ephemeral=True
                )
                await view.wait()

                if view.answer:
                    existing_time.time = time
                    existing_time.time_milliseconds = time_ms
                    existing_time.updated_at = datetime.datetime.utcnow()
                    session.commit()

                    embed.title = f"time saved in {speed.name} {items.name}"
                    embed.description = f"{player.display_name} saved ``{time}`` on **{track_obj.track_name}**"
                else:
                    embed.title = "action canceled"
                    embed.description = "your previous time has not been changed"

                return await interaction.edit_original_response(embed=embed, view=None)
