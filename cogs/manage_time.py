import datetime
import discord
import re

from discord import app_commands
from discord.app_commands import Choice
from autocomplete import track_autocomplete, time_autocomplete
from utils import ConfirmButton, COLLATION
from db import db

import utils


def time_diff(new_time, previous_time):
    diff = datetime.datetime.strptime(
        previous_time, "%M:%S.%f"
    ) - datetime.datetime.strptime(new_time, "%M:%S.%f")
    return (
        f"{diff.seconds // 60}:{diff.seconds % 60:02d}.{diff.microseconds // 1000:03d}"
    )


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(
    speed="the mode you are playing in",
    items="are you using shrooms?",
    track="the track you are playing on",
    time="your time formated like this -> 1:23.456",
)
@app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
@app_commands.autocomplete(track=track_autocomplete, time=time_autocomplete)
async def save_time(
    interaction: discord.Interaction,
    speed: Choice[str],
    items: Choice[str],
    track: str,
    time: app_commands.Range[str, 8, 8],
):
    """save a time"""

    mode = items.value + speed.value + "Tracks"
    embed = discord.Embed(color=0x47E0FF, description="")
    track = await db.Tracks.find_one({"trackName": track}, collation=COLLATION)
    player = interaction.user

    if not track:
        return await interaction.response.send_message(
            content="track not found", ephemeral=True
        )

    if not re.fullmatch("^\\d:[0-5]\\d\\.\\d{3}$", time):
        return await interaction.response.send_message(
            content=f"{time} is not a valid formated time like this (1:23.456)",
            ephemeral=True,
        )

    embed.title = f"time saved in {speed.name} {items.name}"
    embed.description = (
        f"{player.display_name} saved ``{time}`` on **{track['trackName']}**"
    )
    embed.set_thumbnail(url=track["trackUrl"])

    user = await db.Users.find_one({"discordId": player.id})
    if not user:
        user = {
            "discordId": player.id,
            "servers": [{"serverId": interaction.guild.id}],
            mode: [{"trackRef": track["_id"], "time": time}],
        }
        await db.Users.insert_one(user)
        return await interaction.response.send_message(embed=embed)

    if mode not in user:
        user[mode] = []
    previous_time = discord.utils.find(
        lambda x: x["trackRef"] == track["_id"], user[mode]
    )

    if not previous_time:
        user[mode].append({"trackRef": track["_id"], "time": time})
        await db.Users.update_one(
            {"discordId": player.id}, {"$set": {mode: user[mode]}}
        )
        return await interaction.response.send_message(embed=embed)

    elif previous_time["time"] > time:
        embed.description += (
            f"\nyou improved by ``{time_diff(time, previous_time['time'])}`` !"
        )
        user[mode][user[mode].index(previous_time)]["time"] = time
        await db.Users.update_one(
            {"discordId": player.id}, {"$set": {mode: user[mode]}}
        )

    else:
        embed.title = "conflict with previous time"
        embed.description = f"you already have ``{previous_time['time']}`` on this track do you still want to make this change?"
        view = ConfirmButton()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()

        if view.answer:
            user[mode][user[mode].index(previous_time)]["time"] = time
            await db.Users.update_one(
                {"discordId": player.id}, {"$set": {mode: user[mode]}}
            )
            embed.title = f"time saved in {speed.name} {items.name}"
            embed.description = (
                f"{player.display_name} saved ``{time}`` on **{track['trackName']}**"
            )

        else:
            embed.title = "action canceled"
            embed.description = "your previous time as not been changed"

        return await interaction.edit_original_response(embed=embed, view=None)

    return await interaction.response.send_message(embed=embed)


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(
    speed="the mode you played in",
    items="did you use shrooms?",
    track="the track you played on",
)
@app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
@app_commands.autocomplete(track=track_autocomplete)
async def delete_time(
    interaction: discord.Interaction,
    speed: Choice[str],
    items: Choice[str],
    track: str = None,
):
    """delete a time"""

    embed = discord.Embed(color=0x47E0FF, description="", title="deleting times")
    view = ConfirmButton()

    user = await db.Users.find_one({"discordId": interaction.user.id})
    if not user:
        return await interaction.response.send_message(
            content="you have no time to delete", ephemeral=True
        )

    if track:
        track = await db.Tracks.find_one({"trackName": track}, collation=COLLATION)
        if not track:
            return await interaction.response.send_message(
                content="track not found", ephemeral=True
            )
        if track["_id"] not in [
            tracq["trackRef"] for tracq in user[items.value + speed.value + "Tracks"]
        ]:
            return await interaction.response.send_message(
                content="no time to delete", ephemeral=True
            )
        embed.title = f"deleting time on {track['trackName']} {speed.name} {items.name}"
        embed.set_thumbnail(url=track["trackUrl"])
        time = discord.utils.find(
            lambda x: x["trackRef"] == track["_id"],
            user[items.value + speed.value + "Tracks"],
        )["time"]
        embed.description = (
            f"do you want to delete ``{time}`` on **{track['trackName']}**"
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()

        if view.answer:
            user[items.value + speed.value + "Tracks"].remove(
                discord.utils.find(
                    lambda x: x["trackRef"] == track["_id"],
                    user[items.value + speed.value + "Tracks"],
                )
            )
            await db.Users.update_one(
                {"discordId": interaction.user.id},
                {
                    "$set": {
                        items.value
                        + speed.value
                        + "Tracks": user[items.value + speed.value + "Tracks"]
                    }
                },
            )
            embed.title = "time deleted"
            embed.description = (
                f"``{time}`` on **{track['trackName']}** has been deleted"
            )

        else:
            embed.title = "action canceled"
            embed.description = "your time has been left unchanged"

        return await interaction.edit_original_response(embed=embed, view=None)

    embed.title = f"deleting all times in {speed.name} {items.name}"
    embed.description = f"you are about to delete all your times in {speed.name} {items.name}, are you sure you want to do it?"
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    await view.wait()

    if view.answer:
        await db.Users.update_one(
            {"discordId": interaction.user.id},
            {"$set": {items.value + speed.value + "Tracks": []}},
        )
        embed.title = "all times deleted"
        embed.description = (
            f"all your times in {speed.name} {items.name} have been deleted"
        )

    else:
        embed.title = "action canceled"
        embed.description = "your times have been left unchanged"

    return await interaction.edit_original_response(embed=embed, view=None)


async def setup(bot):
    bot.tree.add_command(save_time)
    bot.tree.add_command(delete_time)
