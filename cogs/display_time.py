import discord

from discord import Member, app_commands
from discord.app_commands import Choice
from autocomplete import track_autocomplete
from statistics import mean
from db import db
from utils import COLLATION

import utils


def format_time(total_ms):
    milliseconds = int(total_ms % 1000)
    total_seconds = total_ms // 1000
    seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = total_minutes // 60
    return f"{hours}h {minutes:02}m {seconds:02}s {milliseconds:03}ms"


def player_ranking_in_server(user, mode, users, track):
    users = [
        user
        for user in users
        if user[mode] and track["_id"] in [tracq["trackRef"] for tracq in user[mode]]
    ]
    users = sorted(
        users,
        key=lambda x: discord.utils.find(
            lambda y: y["trackRef"] == track["_id"], x[mode]
        )["time"],
    )
    return f"{users.index(user) + 1}/{len(users)}"


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
):
    """display a specific time, a category or even all times"""

    mode = items.value + speed.value + "Tracks"
    embed = discord.Embed(color=0x47E0FF, description="")
    data = None

    if track:
        track = await db.Tracks.find_one({"trackName": track}, collation=COLLATION)
        if not track:
            return await interaction.response.send_message(
                content="track not found", ephemeral=True
            )

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

    if track:
        if player:
            if mode not in data or track["_id"] not in [
                tracq["trackRef"] for tracq in data[mode]
            ]:
                return await interaction.response.send_message(
                    content="no time to display sorry", ephemeral=True
                )
            else:
                embed.title = f"{track['trackName']} {speed.name} {items.name}"
                embed.set_thumbnail(url=track["trackUrl"])
                member = interaction.guild.get_member(player.id) or f"<@{player.id}>"

                if (
                    isinstance(member, Member)
                    and not interaction.channel.permissions_for(member).send_messages
                ):
                    return await interaction.response.send_message(
                        content="user is missing permission in this channel",
                        ephemeral=True,
                    )

                time = discord.utils.find(
                    lambda x: x["trackRef"] == track["_id"], data[mode]
                )
                embed.description = f"{member.display_name if not isinstance(member, str) else member} - `{time['time']}`"

        else:
            users = await db.Users.find(
                {"servers.serverId": interaction.guild.id, mode: {"$exists": True}}
            ).to_list(None)
            users = [
                user
                for user in users
                if user[mode]
                and track["_id"] in [tracq["trackRef"] for tracq in user[mode]]
            ]
            if data:
                users = list(filter(lambda user: user["discordId"] in data, users))

            if len(users) == 0:
                return await interaction.response.send_message(
                    content="no time to display sorry", ephemeral=True
                )
            else:
                embed.title = f"{track['trackName']} {speed.name} {items.name}"
                embed.set_thumbnail(url=track["trackUrl"])
                rank = 1
                users = sorted(
                    users,
                    key=lambda x: discord.utils.find(
                        lambda y: y["trackRef"] == track["_id"], x[mode]
                    )["time"],
                )
                for user in users:
                    member = (
                        interaction.guild.get_member(user["discordId"])
                        or f"<@{user['discordId']}>"
                    )

                    if (
                        isinstance(member, Member)
                        and not interaction.channel.permissions_for(
                            member
                        ).send_messages
                    ):
                        continue

                    time = discord.utils.find(
                        lambda x: x["trackRef"] == track["_id"], user[mode]
                    )
                    embed.description += f"{rank}. {member.display_name if not isinstance(member, str) else member} - `{time['time']}`\n"
                    rank += 1

                if rank == 1:
                    return await interaction.response.send_message(
                        content="no time to display sorry", ephemeral=True
                    )
    else:
        track_list_raw = await db.Tracks.find({}).to_list(None)
        track_list_raw = sorted(track_list_raw, key=lambda x: x["id"])
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
            total = 0
            embed.title = f"{player.display_name} {speed.name} {items.name}"
            embed.set_thumbnail(url=player.display_avatar)
            if (
                mode not in data
                or len(data[mode]) == 0
                or not interaction.channel.permissions_for(player).send_messages
            ):
                return await interaction.response.send_message(
                    content="No time to display sorry", ephemeral=True
                )

            else:
                users = await db.Users.find(
                    {"servers.serverId": interaction.guild.id, mode: {"$exists": True}}
                ).to_list(None)
                race_ranking = []
                for index, track in enumerate(track_list_raw):
                    if index % 16 == 0:
                        fields.append("")
                    if track["_id"] in [tracq["trackRef"] for tracq in data[mode]]:
                        race_rank_string = player_ranking_in_server(
                            data, mode, users, track
                        )
                        race_ranking.append(int(race_rank_string.split("/")[0]))
                        fields[
                            -1
                        ] += f"**{track['trackName']}**: `{discord.utils.find(lambda x: x['trackRef'] == track['_id'], data[mode])['time']} - {race_rank_string}`\n"
                        time = discord.utils.find(
                            lambda x: x["trackRef"] == track["_id"], data[mode]
                        )["time"]
                        total += (
                            int(time.split(":")[0]) * 60 * 1000
                            + int(time.split(":")[1].split(".")[0]) * 1000
                            + int(time.split(":")[1].split(".")[1])
                        )
                for index, field in enumerate(fields):
                    if len(field) > 0:
                        embed.add_field(name=f"{fields_title[index]}", value=field)
                if len(data[mode]) == len(track_list_raw):
                    embed.set_footer(
                        text=f"total time: {format_time(total)}, average ranking: {round(mean(race_ranking), 1)}"
                    )
                else:
                    embed.set_footer(
                        text=f"average ranking: {round(mean(race_ranking), 1)}"
                    )

        else:
            users = await db.Users.find(
                {"servers.serverId": interaction.guild.id, mode: {"$exists": True}}
            ).to_list(None)
            embed.title = f"{speed.name} {items.name}"
            embed.set_thumbnail(url=interaction.guild.icon)
            if data:
                users = list(filter(lambda user: user["discordId"] in data, users))

            if interaction.guild.chunked:
                users = list(
                    filter(
                        lambda user: interaction.channel.permissions_for(
                            interaction.guild.get_member(user["discordId"])
                        ).send_messages,
                        users,
                    )
                )

            if len(users) == 0:
                return await interaction.response.send_message(
                    content="No time to display sorry", ephemeral=True
                )
            else:
                for index, track in enumerate(track_list_raw):
                    if index % 16 == 0:
                        fields.append("")
                    if any(
                        [
                            track["_id"] in [tracq["trackRef"] for tracq in user[mode]]
                            for user in users
                        ]
                    ):
                        has_track = [
                            user
                            for user in users
                            if user[mode]
                            and track["_id"]
                            in [tracq["trackRef"] for tracq in user[mode]]
                        ]
                        has_best_time = sorted(
                            has_track,
                            key=lambda x: discord.utils.find(
                                lambda y: y["trackRef"] == track["_id"], x[mode]
                            )["time"],
                        )[0]
                        member = (
                            interaction.guild.get_member(has_best_time["discordId"])
                            or f"<@{has_best_time['discordId']}>"
                        )
                        fields[
                            -1
                        ] += f"**{track['trackName']}**: `{discord.utils.find(lambda x: x['trackRef'] == track['_id'], has_best_time[mode])['time']}`\n{member.display_name if not isinstance(member, str) else member}\n"
                for index, field in enumerate(fields):
                    if len(field) > 0:
                        embed.add_field(name=f"{fields_title[index]}", value=field)

    return await interaction.response.send_message(embed=embed)


async def setup(bot):
    bot.tree.add_command(display_time)
