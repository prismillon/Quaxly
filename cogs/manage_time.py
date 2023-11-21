import datetime
import discord
import utils
import sql
import re

from discord import app_commands
from discord.app_commands import Choice
from autocomplete import track_autocomplete, time_autocomplete
from utils import confirmButton


def time_diff(new_time, previous_time):
    diff = datetime.datetime.strptime(previous_time, "%M:%S.%f") - datetime.datetime.strptime(new_time, "%M:%S.%f")
    return f"{diff.seconds // 60}:{diff.seconds % 60:02d}.{diff.microseconds // 1000:03d}"


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(speed="the mode you are playing in", items="are you using shrooms?", track="the track you are playing on", time="your time formated like this -> 1:23.456")
@app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
@app_commands.autocomplete(track=track_autocomplete, time=time_autocomplete)
async def save_time(interaction: discord.Interaction, speed: Choice[str], items: Choice[str], track: str, time: app_commands.Range[str, 8, 8]):
    """save a time"""

    mode = items.value+speed.value
    embed = discord.Embed(color=0x47e0ff, description="")
    track_check = sql.check_track_name(track)
    player = interaction.user

    if mode not in utils.allowed_tables:
        return await interaction.response.send_message(content=":euh:")

    if len(track_check) != 1:
        embed.title = "track not found :("
        embed.description = f"{track} was not found in the list of tracks"
        return await interaction.response.send_message(embed=embed)
    else:
        track = track_check[0][0]

    if not re.fullmatch("^\d:[0-5]\d\\.\d{3}$", time):
        embed.title = "bad time formating >:C"
        embed.description = f"{time} is not a valid formated time like this (1:23.456)"
        return await interaction.response.send_message(embed=embed)

    if len(sql.check_player(player.id)) == 0:
        sql.register_new_player(player.id)

    if len(sql.check_player_server(player.id, interaction.guild_id)) == 0:
        sql.register_user_in_server(player.id, interaction.guild_id)

    previous_time = sql.get_user_track_time(mode, interaction.guild_id, track, player.id)

    embed.set_thumbnail(url=track_check[0][1])
    embed.title = f"time saved in {speed.name} {items.name}"
    embed.description = f"{player.display_name} saved ``{time}`` on **{track}**"

    if len(previous_time) == 0:
        sql.save_time(mode, player.id, track, time)

    elif previous_time[0][2] > time:
        sql.update_time(mode, player.id, track, time)
        embed.description += f"\nyou improved by ``{time_diff(time, previous_time[0][2])}`` !"
        
    else:
        embed.title = "conflict with previous time"
        embed.description = f"you already have ``{previous_time[0][2]}`` on this track do you still want to make this change?"
        view = confirmButton()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()

        if view.answer:
            sql.update_time(mode, player.id, track, time)
            embed.title = f"time saved in {speed.name} {items.name}"
            embed.description = f"{player.display_name} saved ``{time}`` on **{track}**"

        else:
            embed.title = "action canceled"
            embed.description = "your previous time as not been changed"

        return await interaction.edit_original_response(embed=embed, view=None)

    return await interaction.response.send_message(embed=embed)


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(speed="the mode you played in", items="did you use shrooms?", track="the track you played on")
@app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
@app_commands.autocomplete(track=track_autocomplete)
async def delete_time(interaction: discord.Interaction, speed: Choice[str] = None, items: Choice[str] = None, track: str = None):
    """delete a time"""

    embed = discord.Embed(color=0x47e0ff, description="", title="deleting times")
    view = confirmButton()

    if items != None and speed != None:
        table_identifier = items.value+speed.value
    elif items != None:
        table_identifier = items.value
    elif speed != None:
        table_identifier = speed.value
    else:
        table_identifier = "0"
    
    track_identifier = track if track != None else "%"
    embed.description = "you are about to delete listed times, are you sure you want to do it?"

    for mode in filter(lambda table: table_identifier in table, utils.allowed_tables):
        times = sql.get_user_times(mode, interaction.user.id, track_identifier)
        if len(times) > 0:
            content = ""
            for time in times:
                if len(content) < 1000:
                    content += f"**{time[0]}**: `{time[1]}`\n"
                else:
                    content += "**[...]**"
                    break
            embed.add_field(name=mode, value=content)
    
    if len(embed.fields) == 0:
        embed.description = "No time to delete"
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    await view.wait()

    if view.answer:
        for mode in filter(lambda table: table_identifier in table, utils.allowed_tables):
            sql.delete_player_times(mode, interaction.user.id, track_identifier)
        embed.clear_fields()
        embed.description = "selected times have been deleted"

    else:
        embed.title = "action canceled"
        embed.clear_fields()
        embed.description = "your times have been left unchanged"
    
    return await interaction.edit_original_response(embed=embed, view=None)


async def setup(bot):
    bot.tree.add_command(save_time)
    bot.tree.add_command(delete_time)