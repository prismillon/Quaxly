import discord

from discord import app_commands
from discord.app_commands import Choice
from .autocomplete import dx_track_autocomplete
from utils import ConfirmButton
from database import get_db_session
from models import User, Track, TimeRecord, GAME_MK8DX
from game_utils import get_track_by_name, get_user_times_for_game
import utils


class DeleteTimeCommands:
    """Delete time command for MK8DX"""

    @app_commands.command(name="delete_time")
    @app_commands.guild_only()
    @app_commands.describe(
        speed="the mode you played in",
        items="did you use shrooms?",
        track="the track you played on",
    )
    @app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
    @app_commands.autocomplete(track=dx_track_autocomplete)
    async def delete_time(
        self,
        interaction: discord.Interaction,
        speed: Choice[str],
        items: Choice[str],
        track: str = None,
    ):
        """Delete a time for MK8DX"""

        game = GAME_MK8DX
        race_type = items.value
        speed_value = int(speed.value)

        embed = discord.Embed(color=0x47E0FF, description="", title="deleting times")
        view = ConfirmButton()

        with get_db_session() as session:
            user = (
                session.query(User)
                .filter(User.discord_id == interaction.user.id)
                .first()
            )
            if not user:
                return await interaction.response.send_message(
                    content="you have no time to delete", ephemeral=True
                )

            if track:
                track_obj = get_track_by_name(session, game, track)
                if not track_obj:
                    return await interaction.response.send_message(
                        content="track not found", ephemeral=True
                    )

                time_record = (
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

                if not time_record:
                    return await interaction.response.send_message(
                        content="no time to delete", ephemeral=True
                    )

                embed.title = (
                    f"deleting time on {track_obj.track_name} {speed.name} {items.name}"
                )
                embed.set_thumbnail(url=track_obj.track_url)
                embed.description = f"do you want to delete ``{time_record.time}`` on **{track_obj.track_name}**"

                await interaction.response.send_message(
                    embed=embed, view=view, ephemeral=True
                )
                await view.wait()

                if view.answer:
                    session.delete(time_record)
                    session.commit()

                    embed.title = "time deleted"
                    embed.description = f"``{time_record.time}`` on **{track_obj.track_name}** has been deleted"
                else:
                    embed.title = "action canceled"
                    embed.description = "your time has been left unchanged"

                return await interaction.edit_original_response(embed=embed, view=None)

            else:
                time_records = (
                    session.query(TimeRecord)
                    .filter(
                        TimeRecord.user_id == user.id,
                        TimeRecord.game == game,
                        TimeRecord.race_type == race_type,
                        TimeRecord.speed == speed_value,
                    )
                    .all()
                )

                if not time_records:
                    return await interaction.response.send_message(
                        content="you have no times to delete in this mode",
                        ephemeral=True,
                    )

                embed.title = f"deleting all times in {speed.name} {items.name}"
                embed.description = f"you are about to delete all your times in {speed.name} {items.name}, are you sure you want to do it?"

                await interaction.response.send_message(
                    embed=embed, view=view, ephemeral=True
                )
                await view.wait()

                if view.answer:
                    for time_record in time_records:
                        session.delete(time_record)
                    session.commit()

                    embed.title = "all times deleted"
                    embed.description = (
                        f"all your times in {speed.name} {items.name} have been deleted"
                    )
                else:
                    embed.title = "action canceled"
                    embed.description = "your times have been left unchanged"

                return await interaction.edit_original_response(embed=embed, view=None)
