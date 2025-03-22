import discord

from discord import Member, app_commands
from discord.ext import commands
from discord.app_commands import Choice
from autocomplete import track_autocomplete
from statistics import mean
from db import db
from utils import COLLATION

import utils


def format_time(total_ms: int) -> str:
    hours = total_ms // (1000 * 60 * 60)
    minutes = (total_ms % (1000 * 60 * 60)) // (1000 * 60)
    seconds = (total_ms % (1000 * 60)) // 1000
    milliseconds = total_ms % 1000

    return f"{hours}h {minutes:02}m {seconds:02}s {milliseconds:03}ms"


def parse_time_to_ms(time_str: str) -> int:
    """Convert a time string in format MM:SS.mmm to milliseconds"""
    minutes, seconds_ms = time_str.split(":")
    seconds, milliseconds = seconds_ms.split(".")

    return (int(minutes) * 60 * 1000) + (int(seconds) * 1000) + int(milliseconds)


def get_track_time(user_data: dict, track_id: str, mode: str) -> dict:
    """Get time data for a specific track from user data"""
    return discord.utils.find(lambda x: x["trackRef"] == track_id, user_data[mode])


def has_track(user_data: dict, track_id: str, mode: str) -> bool:
    """Check if user has a time for a specific track"""
    return mode in user_data and track_id in [
        tracq["trackRef"] for tracq in user_data[mode]
    ]


def get_member_display(interaction: discord.Interaction, user_id: int) -> str:
    """Get display name for a member, falling back to mention if not found"""
    member = interaction.guild.get_member(user_id)
    return member.display_name if member else f"<@{user_id}>"


def can_send_messages(interaction: discord.Interaction, member: Member) -> bool:
    """Check if a member can send messages in the current channel"""
    return (
        not isinstance(member, Member)
        or interaction.channel.permissions_for(member).send_messages
    )


def filter_users_with_track(users: list, track_id: str, mode: str) -> list:
    """Filter users who have a time for a specific track"""
    return [
        user
        for user in users
        if user[mode] and track_id in [tracq["trackRef"] for tracq in user[mode]]
    ]


def get_track_fields() -> list:
    """Get the list of track field titles"""
    return [
        "__Nitro tracks__",
        "__Retro tracks__",
        "__DLC tracks__",
        "__Wave 1 & 2__",
        "__Wave 3 & 4__",
        "__Wave 5 & 6__",
    ]


def player_ranking_in_server(user: dict, mode: str, users: list, track: dict) -> str:
    """Get player's ranking for a specific track"""
    users = filter_users_with_track(users, track["_id"], mode)
    users = sorted(
        users,
        key=lambda x: get_track_time(x, track["_id"], mode)["time"],
    )
    return f"{users.index(user) + 1}/{len(users)}"


async def display_single_track_single_player(
    interaction: discord.Interaction,
    embed: discord.Embed,
    track: dict,
    player: discord.Member,
    data: dict,
    mode: str,
) -> discord.InteractionResponse:
    """Display times for a single track and single player"""
    if not has_track(data, track["_id"], mode):
        return await interaction.response.send_message(
            content="no time to display sorry", ephemeral=True
        )

    embed.title = f"{track['trackName']} {mode.replace('Tracks', '')}"
    embed.set_thumbnail(url=track["trackUrl"])
    member = interaction.guild.get_member(player.id) or f"<@{player.id}>"

    if not can_send_messages(interaction, member):
        return await interaction.response.send_message(
            content="user is missing permission in this channel",
            ephemeral=True,
        )

    time = get_track_time(data, track["_id"], mode)
    embed.description = (
        f"{get_member_display(interaction, player.id)} - `{time['time']}`"
    )
    return await interaction.response.send_message(embed=embed)


async def display_single_track_all_players(
    interaction: discord.Interaction,
    embed: discord.Embed,
    track: dict,
    data: list,
    mode: str,
    users: list,
) -> discord.InteractionResponse:
    """Display times for a single track and all players"""
    users = filter_users_with_track(users, track["_id"], mode)

    if data:
        users = list(filter(lambda user: user["discordId"] in data, users))

    if not users:
        return await interaction.response.send_message(
            content="no time to display sorry", ephemeral=True
        )

    embed.title = f"{track['trackName']} {mode.replace('Tracks', '')}"
    embed.set_thumbnail(url=track["trackUrl"])
    users = sorted(
        users,
        key=lambda x: get_track_time(x, track["_id"], mode)["time"],
    )

    valid_entries = 0
    for rank, user in enumerate(users, 1):
        member = interaction.guild.get_member(user["discordId"])
        if not can_send_messages(interaction, member):
            continue

        time = get_track_time(user, track["_id"], mode)
        embed.description += f"{rank}. {get_member_display(interaction, user['discordId'])} - `{time['time']}`\n"
        valid_entries += 1

    if valid_entries == 0:
        return await interaction.response.send_message(
            content="no time to display sorry", ephemeral=True
        )

    return await interaction.response.send_message(embed=embed)


async def display_all_tracks_single_player(
    interaction: discord.Interaction,
    embed: discord.Embed,
    player: discord.Member,
    data: dict,
    mode: str,
    track_list_raw: list,
) -> discord.InteractionResponse:
    """Display all tracks for a single player"""
    total = 0
    embed.title = f"{player.display_name} {mode.replace('Tracks', '')}"
    embed.set_thumbnail(url=player.display_avatar)

    if not has_track(data, track_list_raw[0]["_id"], mode) or not can_send_messages(
        interaction, player
    ):
        return await interaction.response.send_message(
            content="No time to display sorry", ephemeral=True
        )

    users = await db.Users.find(
        {"servers.serverId": interaction.guild.id, mode: {"$exists": True}}
    ).to_list(None)
    race_ranking = []
    fields = []
    fields_title = get_track_fields()

    for index, track in enumerate(track_list_raw):
        if index % 16 == 0:
            fields.append("")
        if has_track(data, track["_id"], mode):
            race_rank_string = player_ranking_in_server(data, mode, users, track)
            race_ranking.append(int(race_rank_string.split("/")[0]))

            time = get_track_time(data, track["_id"], mode)["time"]
            fields[-1] += f"**{track['trackName']}**: `{time} - {race_rank_string}`\n"
            total += parse_time_to_ms(time)

    for index, field in enumerate(fields):
        if field:
            embed.add_field(name=fields_title[index], value=field)

    if len(data[mode]) == len(track_list_raw):
        embed.set_footer(
            text=f"total time: {format_time(total)}, average ranking: {round(mean(race_ranking), 1)}"
        )
    else:
        embed.set_footer(text=f"average ranking: {round(mean(race_ranking), 1)}")

    return await interaction.response.send_message(embed=embed)


async def display_all_tracks_all_players(
    interaction: discord.Interaction,
    embed: discord.Embed,
    data: list,
    mode: str,
    track_list_raw: list,
) -> discord.InteractionResponse:
    """Display all tracks for all players"""
    users = await db.Users.find(
        {"servers.serverId": interaction.guild.id, mode: {"$exists": True}}
    ).to_list(None)
    embed.title = f"{mode.replace('Tracks', '')}"
    embed.set_thumbnail(url=interaction.guild.icon)

    if data:
        users = list(filter(lambda user: user["discordId"] in data, users))

    if interaction.guild.chunked:
        users = list(
            filter(
                lambda user: can_send_messages(
                    interaction, interaction.guild.get_member(user["discordId"])
                ),
                users,
            )
        )

    if not users:
        return await interaction.response.send_message(
            content="No time to display sorry", ephemeral=True
        )

    fields = []
    fields_title = get_track_fields()

    for index, track in enumerate(track_list_raw):
        if index % 16 == 0:
            fields.append("")

        track_users = filter_users_with_track(users, track["_id"], mode)
        if track_users:
            best_user = sorted(
                track_users,
                key=lambda x: get_track_time(x, track["_id"], mode)["time"],
            )[0]

            best_time = get_track_time(best_user, track["_id"], mode)["time"]
            fields[
                -1
            ] += f"**{track['trackName']}**: `{best_time}`\n{get_member_display(interaction, best_user['discordId'])}\n"

    for index, field in enumerate(fields):
        if field:
            embed.add_field(name=fields_title[index], value=field)

    return await interaction.response.send_message(embed=embed)


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(
    speed="the mode you want to display",
    items="do you want to only display times with shrooms or without?",
    track="the track you want to display",
    player="the player you want to display",
)
@app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
@app_commands.autocomplete(track=track_autocomplete)
async def display_time(
    interaction: discord.Interaction,
    speed: Choice[str],
    items: Choice[str],
    track: str = None,
    player: discord.Member | discord.Role = None,
) -> None:
    """display a specific time, a category or even all times"""

    mode = items.value + speed.value + "Tracks"
    embed = discord.Embed(color=0x47E0FF, description="")
    data = None

    # Get track if specified
    if track:
        track = await db.Tracks.find_one({"trackName": track}, collation=COLLATION)
        if not track:
            return await interaction.response.send_message(
                content="track not found", ephemeral=True
            )

    # Handle player or role members
    if player:
        if isinstance(player, discord.Member):
            data = await db.Users.find_one({"discordId": player.id})
            if not data or interaction.guild.id not in [
                server["serverId"] for server in data["servers"]
            ]:
                return await interaction.response.send_message(
                    content="player is not registered in the server", ephemeral=True
                )
        elif isinstance(player, discord.Role):
            data = [user.id for user in player.members]
            player = None
        else:
            return await interaction.response.send_message(
                content="an error occured please report this", ephemeral=True
            )

    # Different display modes
    if track and player and isinstance(player, discord.Member):
        # Single track, single player
        return await display_single_track_single_player(
            interaction, embed, track, player, data, mode
        )
    elif track:
        # Single track, all players (or filtered by role)
        users = await db.Users.find(
            {"servers.serverId": interaction.guild.id, mode: {"$exists": True}}
        ).to_list(None)
        return await display_single_track_all_players(
            interaction, embed, track, data, mode, users
        )
    else:
        # All tracks
        track_list_raw = await db.Tracks.find({}).to_list(None)
        track_list_raw = sorted(track_list_raw, key=lambda x: x["id"])

        if player and isinstance(player, discord.Member):
            # All tracks, single player
            return await display_all_tracks_single_player(
                interaction, embed, player, data, mode, track_list_raw
            )
        else:
            # All tracks, all players (or filtered by role)
            return await display_all_tracks_all_players(
                interaction, embed, data, mode, track_list_raw
            )


async def setup(bot: commands.Bot) -> None:
    bot.tree.add_command(display_time)
