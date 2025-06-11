import discord
from statistics import mean

from discord import Member, app_commands
from discord.app_commands import Choice
from .autocomplete import dx_track_autocomplete
from database import get_db_session
from models import User, Track, TimeRecord, UserServer, GAME_MK8DX
from game_utils import get_track_by_name, get_game_tracks
import utils


def format_time(total_ms):
    """Format milliseconds to readable time"""
    milliseconds = int(total_ms % 1000)
    total_seconds = total_ms // 1000
    seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = total_minutes // 60
    return f"{hours}h {minutes:02}m {seconds:02}s {milliseconds:03}ms"


def get_player_ranking_in_server(
    session, user_id, track_id, game, race_type, speed, server_id
):
    """Get player's ranking for a specific track in the server"""
    server_times = (
        session.query(TimeRecord)
        .join(User)
        .join(UserServer)
        .filter(
            UserServer.server_id == server_id,
            TimeRecord.track_id == track_id,
            TimeRecord.game == game,
            TimeRecord.race_type == race_type,
            TimeRecord.speed == speed,
        )
        .order_by(TimeRecord.time_milliseconds)
        .all()
    )

    if not server_times:
        return "1/1"

    for i, time_record in enumerate(server_times):
        if time_record.user_id == user_id:
            return f"{i + 1}/{len(server_times)}"

    return "N/A"


class DisplayTimeCommands:
    """Display time command for MK8DX"""

    @app_commands.command(name="display_time")
    @app_commands.guild_only()
    @app_commands.describe(
        speed="the mode you want to display",
        items="do you want to only display times with shrooms or without?",
        track="the track you want to display",
        player="the player you want to display",
    )
    @app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
    @app_commands.autocomplete(track=dx_track_autocomplete)
    async def display_time(
        self,
        interaction: discord.Interaction,
        speed: Choice[str],
        items: Choice[str],
        track: str = None,
        player: discord.Member | discord.Role = None,
    ):
        """Display a specific time, a category or even all times for MK8DX"""

        game = GAME_MK8DX
        race_type = items.value
        speed_value = int(speed.value)

        embed = discord.Embed(color=0x47E0FF, description="")

        with get_db_session() as session:
            track_obj = None
            if track:
                track_obj = get_track_by_name(session, game, track)
                if not track_obj:
                    return await interaction.response.send_message(
                        content="track not found", ephemeral=True
                    )

            role_member_ids = None
            if isinstance(player, discord.Role):
                role_member_ids = [member.id for member in player.members]
                player = None

            if track_obj:
                if player:
                    user = (
                        session.query(User).filter(User.discord_id == player.id).first()
                    )
                    if not user:
                        return await interaction.response.send_message(
                            content="player is not registered", ephemeral=True
                        )

                    user_server = (
                        session.query(UserServer)
                        .filter(
                            UserServer.user_id == user.id,
                            UserServer.server_id == interaction.guild.id,
                        )
                        .first()
                    )
                    if not user_server:
                        return await interaction.response.send_message(
                            content="player is not registered in the server",
                            ephemeral=True,
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
                            content="no time to display sorry", ephemeral=True
                        )

                    embed.title = f"{track_obj.track_name} {speed.name} {items.name}"
                    embed.set_thumbnail(url=track_obj.track_url)

                    member = (
                        interaction.guild.get_member(player.id) or f"<@{player.id}>"
                    )
                    if (
                        isinstance(member, Member)
                        and not interaction.channel.permissions_for(
                            member
                        ).send_messages
                    ):
                        return await interaction.response.send_message(
                            content="user is missing permission in this channel",
                            ephemeral=True,
                        )

                    embed.description = f"{member.display_name if not isinstance(member, str) else member} - `{time_record.time}`"

                else:
                    query = (
                        session.query(TimeRecord)
                        .join(User)
                        .join(UserServer)
                        .filter(
                            UserServer.server_id == interaction.guild.id,
                            TimeRecord.track_id == track_obj.id,
                            TimeRecord.game == game,
                            TimeRecord.race_type == race_type,
                            TimeRecord.speed == speed_value,
                        )
                        .order_by(TimeRecord.time_milliseconds)
                    )

                    if role_member_ids:
                        query = query.filter(User.discord_id.in_(role_member_ids))

                    time_records = query.all()

                    if not time_records:
                        return await interaction.response.send_message(
                            content="no time to display sorry", ephemeral=True
                        )

                    embed.title = f"{track_obj.track_name} {speed.name} {items.name}"
                    embed.set_thumbnail(url=track_obj.track_url)

                    rank = 1
                    for time_record in time_records:
                        member = (
                            interaction.guild.get_member(time_record.user.discord_id)
                            or f"<@{time_record.user.discord_id}>"
                        )

                        if (
                            isinstance(member, Member)
                            and not interaction.channel.permissions_for(
                                member
                            ).send_messages
                        ):
                            continue

                        embed.description += f"{rank}. {member.display_name if not isinstance(member, str) else member} - `{time_record.time}`\n"
                        rank += 1

                    if rank == 1:
                        return await interaction.response.send_message(
                            content="no time to display sorry", ephemeral=True
                        )

            else:
                all_tracks = get_game_tracks(session, game)
                all_tracks = sorted(all_tracks, key=lambda x: x.track_id)

                fields = []
                fields_title = [
                    "__Nitro tracks__",
                    "__Retro tracks__",
                    "__DLC tracks__",
                    "__Wave 1 & 2__",
                    "__Wave 3 & 4__",
                    "__Wave 5 & 6__",
                ]

                if player:
                    user = (
                        session.query(User).filter(User.discord_id == player.id).first()
                    )
                    if not user:
                        return await interaction.response.send_message(
                            content="player is not registered", ephemeral=True
                        )

                    user_server = (
                        session.query(UserServer)
                        .filter(
                            UserServer.user_id == user.id,
                            UserServer.server_id == interaction.guild.id,
                        )
                        .first()
                    )
                    if not user_server:
                        return await interaction.response.send_message(
                            content="player is not registered in the server",
                            ephemeral=True,
                        )

                    if not interaction.channel.permissions_for(player).send_messages:
                        return await interaction.response.send_message(
                            content="No time to display sorry", ephemeral=True
                        )

                    user_times = (
                        session.query(TimeRecord)
                        .filter(
                            TimeRecord.user_id == user.id,
                            TimeRecord.game == game,
                            TimeRecord.race_type == race_type,
                            TimeRecord.speed == speed_value,
                        )
                        .all()
                    )

                    if not user_times:
                        return await interaction.response.send_message(
                            content="No time to display sorry", ephemeral=True
                        )

                    total = 0
                    race_ranking = []
                    embed.title = f"{player.display_name} {speed.name} {items.name}"
                    embed.set_thumbnail(url=player.display_avatar)

                    user_times_dict = {tr.track_id: tr for tr in user_times}

                    for index, track in enumerate(all_tracks):
                        if index % 16 == 0:
                            fields.append("")

                        if track.id in user_times_dict:
                            time_record = user_times_dict[track.id]
                            race_rank_string = get_player_ranking_in_server(
                                session,
                                user.id,
                                track.id,
                                game,
                                race_type,
                                speed_value,
                                interaction.guild.id,
                            )
                            race_ranking.append(int(race_rank_string.split("/")[0]))
                            fields[
                                -1
                            ] += f"**{track.track_name}**: `{time_record.time} - {race_rank_string}`\n"
                            total += time_record.time_milliseconds

                    for index, field in enumerate(fields):
                        if len(field) > 0:
                            embed.add_field(name=f"{fields_title[index]}", value=field)

                    if len(user_times) == len(all_tracks):
                        embed.set_footer(
                            text=f"total time: {format_time(total)}, average ranking: {round(mean(race_ranking), 1)}"
                        )
                    elif race_ranking:
                        embed.set_footer(
                            text=f"average ranking: {round(mean(race_ranking), 1)}"
                        )

                else:
                    embed.title = f"{speed.name} {items.name}"
                    embed.set_thumbnail(url=interaction.guild.icon)

                    for index, track in enumerate(all_tracks):
                        if index % 16 == 0:
                            fields.append("")

                        query = (
                            session.query(TimeRecord)
                            .join(User)
                            .join(UserServer)
                            .filter(
                                UserServer.server_id == interaction.guild.id,
                                TimeRecord.track_id == track.id,
                                TimeRecord.game == game,
                                TimeRecord.race_type == race_type,
                                TimeRecord.speed == speed_value,
                            )
                            .order_by(TimeRecord.time_milliseconds)
                        )

                        if role_member_ids:
                            query = query.filter(User.discord_id.in_(role_member_ids))

                        best_time = query.first()

                        if best_time:
                            member = (
                                interaction.guild.get_member(best_time.user.discord_id)
                                or f"<@{best_time.user.discord_id}>"
                            )
                            fields[
                                -1
                            ] += f"**{track.track_name}**: `{best_time.time}`\n{member.display_name if not isinstance(member, str) else member}\n"

                    for index, field in enumerate(fields):
                        if len(field) > 0:
                            embed.add_field(name=f"{fields_title[index]}", value=field)

        return await interaction.response.send_message(embed=embed)
