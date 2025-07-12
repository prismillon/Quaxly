import datetime
import discord
import re
from statistics import mean

from discord import app_commands
from discord.app_commands import Choice
from database import get_db_session
from models import Track, TimeRecord, User, GAME_MKWORLD, UserServer
from game_utils import get_game_tracks
from utils import ConfirmButton, itemChoices


def time_diff(new_time, previous_time):
    """Calculate time difference between two time strings"""
    diff = datetime.datetime.strptime(
        previous_time, "%M:%S.%f"
    ) - datetime.datetime.strptime(new_time, "%M:%S.%f")
    return (
        f"{diff.seconds // 60}:{diff.seconds % 60:02d}.{diff.microseconds // 1000:03d}"
    )


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


async def track_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """Autocomplete for MKWorld track names"""
    with get_db_session() as session:
        tracks = get_game_tracks(session, GAME_MKWORLD)

        if current:
            filtered_tracks = [
                track
                for track in tracks
                if current.lower() in track.track_name.lower()
                or current.lower() in track.full_name.lower()
            ]
        else:
            filtered_tracks = tracks

        filtered_tracks = sorted(filtered_tracks, key=lambda x: x.track_id)[:25]

        return [
            app_commands.Choice(
                name=f"{track.track_name} - {track.full_name}", value=track.track_name
            )
            for track in filtered_tracks
        ]


async def time_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    """Format time input for MKWorld (150cc only)"""
    if len(current) == 0:
        return [app_commands.Choice(name="Format: 1:23.456", value="Format: 1:23.456")]
    elif len(current) == 6:
        current = current[:1] + ":" + current[1:3] + "." + current[3:]
        return [app_commands.Choice(name=current, value=current)]
    elif len(current) == 8:
        current = current[:1] + ":" + current[2:4] + "." + current[5:]
        return [app_commands.Choice(name=current, value=current)]
    else:
        return [app_commands.Choice(name=current, value=current)]


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(
    items="are you using shrooms?",
    track="the track you are playing on",
    time="your time formatted like this -> 1:23.456",
)
@app_commands.choices(items=itemChoices)
@app_commands.autocomplete(track=track_autocomplete, time=time_autocomplete)
async def save_time(
    interaction: discord.Interaction,
    items: Choice[str],
    track: str,
    time: app_commands.Range[str, 8, 8],
):
    """Save a time for Mario Kart World (150cc only)"""

    embed = discord.Embed(color=0x47E0FF, description="")
    player = interaction.user

    if not re.fullmatch("^\\d:[0-5]\\d\\.\\d{3}$", time):
        return await interaction.response.send_message(
            content=f"{time} is not a valid formatted time like this (1:23.456)",
            ephemeral=True,
        )

    with get_db_session() as session:
        track_obj = (
            session.query(Track)
            .filter(Track.game == GAME_MKWORLD, Track.track_name == track)
            .first()
        )

        if not track_obj:
            return await interaction.response.send_message(
                content="Track not found", ephemeral=True
            )

        user = session.query(User).filter(User.discord_id == player.id).first()

        if not user:
            user = User(discord_id=player.id)
            session.add(user)
            session.commit()

        existing_record = (
            session.query(TimeRecord)
            .filter(
                TimeRecord.user_id == user.id,
                TimeRecord.track_id == track_obj.id,
                TimeRecord.game == GAME_MKWORLD,
                TimeRecord.race_type == items.value,
                TimeRecord.speed == 150,
            )
            .first()
        )

        embed.title = f"Time saved in 150cc {items.name}"
        embed.description = (
            f"{player.display_name} saved ``{time}`` on **{track_obj.full_name}**"
        )
        embed.set_thumbnail(url=track_obj.track_url)

        time_ms = TimeRecord.time_to_milliseconds(time)

        if not existing_record:
            new_record = TimeRecord(
                user_id=user.id,
                track_id=track_obj.id,
                game=GAME_MKWORLD,
                time=time,
                race_type=items.value,
                speed=150,
                time_milliseconds=time_ms,
            )
            session.add(new_record)
            session.commit()
            return await interaction.response.send_message(embed=embed)

        elif existing_record.time_milliseconds > time_ms:
            embed.description += (
                f"\nYou improved by ``{time_diff(time, existing_record.time)}``!"
            )
            existing_record.time = time
            existing_record.time_milliseconds = time_ms
            session.commit()

        else:
            embed.title = "Conflict with previous time"
            embed.description = f"You already have ``{existing_record.time}`` on this track. Do you still want to make this change?"
            view = ConfirmButton()
            await interaction.response.send_message(
                embed=embed, view=view, ephemeral=True
            )
            await view.wait()

            if view.answer:
                existing_record.time = time
                existing_record.time_milliseconds = time_ms
                session.commit()
                embed.title = f"Time saved in 150cc {items.name}"
                embed.description = f"{player.display_name} saved ``{time}`` on **{track_obj.full_name}**"
            else:
                embed.title = "Action canceled"
                embed.description = "Your previous time has not been changed"

            return await interaction.edit_original_response(embed=embed, view=None)

    return await interaction.response.send_message(embed=embed)


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(
    items="did you use shrooms?",
    track="the track you played on",
)
@app_commands.choices(items=itemChoices)
@app_commands.autocomplete(track=track_autocomplete)
async def delete_time(
    interaction: discord.Interaction,
    items: Choice[str],
    track: str = None,
):
    """Delete a time for Mario Kart World"""

    embed = discord.Embed(color=0x47E0FF, description="", title="Deleting times")
    view = ConfirmButton()

    with get_db_session() as session:
        user = (
            session.query(User).filter(User.discord_id == interaction.user.id).first()
        )

        if not user:
            return await interaction.response.send_message(
                content="You have no times to delete", ephemeral=True
            )

        if track:
            track_obj = (
                session.query(Track)
                .filter(Track.game == GAME_MKWORLD, Track.track_name == track)
                .first()
            )

            if not track_obj:
                return await interaction.response.send_message(
                    content="Track not found", ephemeral=True
                )

            time_record = (
                session.query(TimeRecord)
                .filter(
                    TimeRecord.user_id == user.id,
                    TimeRecord.track_id == track_obj.id,
                    TimeRecord.game == GAME_MKWORLD,
                    TimeRecord.race_type == items.value,
                    TimeRecord.speed == 150,
                )
                .first()
            )

            if not time_record:
                return await interaction.response.send_message(
                    content="No time to delete", ephemeral=True
                )

            embed.title = f"Deleting time on {track_obj.full_name} 150cc {items.name}"
            embed.set_thumbnail(url=track_obj.track_url)
            embed.description = f"Do you want to delete ``{time_record.time}`` on **{track_obj.full_name}**?"
            await interaction.response.send_message(
                embed=embed, view=view, ephemeral=True
            )
            await view.wait()

            if view.answer:
                session.delete(time_record)
                session.commit()
                embed.title = "Time deleted"
                embed.description = f"``{time_record.time}`` on **{track_obj.full_name}** has been deleted"
            else:
                embed.title = "Action canceled"
                embed.description = "Your time has been left unchanged"

        else:
            time_records = (
                session.query(TimeRecord)
                .filter(
                    TimeRecord.user_id == user.id,
                    TimeRecord.game == GAME_MKWORLD,
                    TimeRecord.race_type == items.value,
                    TimeRecord.speed == 150,
                )
                .all()
            )

            if not time_records:
                return await interaction.response.send_message(
                    content="You have no times to delete in this category",
                    ephemeral=True,
                )

            embed.title = f"Deleting all times in 150cc {items.name}"
            embed.description = f"You are about to delete all your times in 150cc {items.name}. Are you sure you want to do it?"
            await interaction.response.send_message(
                embed=embed, view=view, ephemeral=True
            )
            await view.wait()

            if view.answer:
                for record in time_records:
                    session.delete(record)
                session.commit()
                embed.title = "All times deleted"
                embed.description = (
                    f"All your times in 150cc {items.name} have been deleted"
                )
            else:
                embed.title = "Action canceled"
                embed.description = "Your times have been left unchanged"

        return await interaction.edit_original_response(embed=embed, view=None)


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(
    items="did you use shrooms?",
    track="the track you want to see times for",
    player="the player you want to display",
)
@app_commands.choices(items=itemChoices)
@app_commands.autocomplete(track=track_autocomplete)
async def display_time(
    interaction: discord.Interaction,
    items: Choice[str],
    track: str = None,
    player: discord.Member | discord.Role = None,
):
    """Display your times for Mario Kart World"""

    game = GAME_MKWORLD
    race_type = items.value
    speed_value = 150

    embed = discord.Embed(color=0x47E0FF, description="")

    with get_db_session() as session:
        track_obj = None
        if track:
            track_obj = (
                session.query(Track)
                .filter(Track.game == GAME_MKWORLD, Track.track_name == track)
                .first()
            )
            if not track_obj:
                return await interaction.response.send_message(
                    content="Track not found", ephemeral=True
                )

        role_member_ids = None
        if isinstance(player, discord.Role):
            role_member_ids = [member.id for member in player.members]
            player = None

        if track_obj:
            if player:
                user = session.query(User).filter(User.discord_id == player.id).first()
                if not user:
                    return await interaction.response.send_message(
                        content="Player is not registered", ephemeral=True
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
                        content="Player is not registered in the server",
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
                        content="No time to display sorry", ephemeral=True
                    )

                embed.title = f"{track_obj.track_name} - 150cc {items.name}"
                embed.set_thumbnail(url=track_obj.track_url)

                member = interaction.guild.get_member(player.id) or f"<@{player.id}>"
                if (
                    isinstance(member, discord.Member)
                    and not interaction.channel.permissions_for(member).send_messages
                ):
                    return await interaction.response.send_message(
                        content="User is missing permission in this channel",
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
                        content="No time to display sorry", ephemeral=True
                    )

                embed.title = f"{track_obj.track_name} - 150cc {items.name}"
                embed.set_thumbnail(url=track_obj.track_url)

                rank = 1
                for time_record in time_records:
                    member = (
                        interaction.guild.get_member(time_record.user.discord_id)
                        or f"<@{time_record.user.discord_id}>"
                    )

                    if (
                        isinstance(member, discord.Member)
                        and not interaction.channel.permissions_for(
                            member
                        ).send_messages
                    ):
                        continue

                    embed.description += f"{rank}. {member.display_name if not isinstance(member, str) else member} - `{time_record.time}`\n"
                    rank += 1

                if rank == 1:
                    return await interaction.response.send_message(
                        content="No time to display sorry", ephemeral=True
                    )

        else:
            all_tracks = get_game_tracks(session, game)
            all_tracks = sorted(all_tracks, key=lambda x: x.track_id)

            fields = []
            fields_title = []

            cups_dict = {}
            for track in all_tracks:
                cup_name = track.cup.cup_name
                if cup_name not in cups_dict:
                    cups_dict[cup_name] = []
                cups_dict[cup_name].append(track)

            sorted_cups = sorted(
                cups_dict.items(), key=lambda x: min(t.track_id for t in x[1])
            )

            if player:
                user = session.query(User).filter(User.discord_id == player.id).first()
                if not user:
                    return await interaction.response.send_message(
                        content="Player is not registered", ephemeral=True
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
                        content="Player is not registered in the server",
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
                embed.title = (
                    f"{player.display_name} MKWorld Times - 150cc {items.name}"
                )
                embed.set_thumbnail(url=player.display_avatar)

                user_times_dict = {tr.track_id: tr for tr in user_times}

                for cup_name, cup_tracks in sorted_cups:
                    field_content = ""
                    for track in cup_tracks:
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
                            field_content += f"**{track.track_name}**: `{time_record.time} - {race_rank_string}`\n"
                            total += time_record.time_milliseconds

                    if field_content:
                        embed.add_field(
                            name=f"__{cup_name}__", value=field_content, inline=False
                        )

                if len(user_times) == len(all_tracks):
                    embed.set_footer(
                        text=f"Total time: {format_time(total)}, Average ranking: {round(mean(race_ranking), 1)}"
                    )
                elif race_ranking:
                    embed.set_footer(
                        text=f"Average ranking: {round(mean(race_ranking), 1)}"
                    )

            else:
                embed.title = f"MKWorld Server Overview - 150cc {items.name}"
                embed.set_thumbnail(url=interaction.guild.icon)

                for cup_name, cup_tracks in sorted_cups:
                    field_content = ""
                    for track in cup_tracks:
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
                            field_content += f"**{track.track_name}**: `{best_time.time}`\n{member.display_name if not isinstance(member, str) else member}\n"

                    if field_content:
                        embed.add_field(
                            name=f"__{cup_name}__", value=field_content, inline=False
                        )

                if not embed.fields:
                    return await interaction.response.send_message(
                        content="No times to display sorry", ephemeral=True
                    )

    return await interaction.response.send_message(embed=embed)


async def setup(bot):
    bot.tree.add_command(save_time)
    bot.tree.add_command(delete_time)
    bot.tree.add_command(display_time)
