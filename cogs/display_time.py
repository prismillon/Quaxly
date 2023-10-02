import discord
import utils
import sql

from discord import app_commands
from discord.app_commands import Choice
from autocomplete import track_autocomplete


def format_time(total_ms):
    milliseconds = int(total_ms % 1000)
    total_seconds = total_ms // 1000
    seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = total_minutes // 60
    return f'{hours}h {minutes:02}m {seconds:02}s {milliseconds:03}ms'


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(speed="the mode you want to display", items="do you want to only display times with shrooms or without?", track="the track you want to display", player="the player you want to display")
@app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
@app_commands.autocomplete(track=track_autocomplete)
async def display_time(interaction: discord.Interaction, speed: Choice[str], items: Choice[str], track: str = None, player: discord.Member = None):
    """display a specific time, a category or even all times"""

    if not interaction.guild.chunked:
        return await utils.wait_for_chunk(interaction)

    mode = items.value+speed.value
    embed = discord.Embed(color=0x47e0ff, description="")
    
    if mode not in utils.allowed_tables:
        return await interaction.response.send_message(content=":euh:")

    if track and len(sql.check_track_name(track)) != 1:
        embed.title = "track not found :("
        embed.description = f"{track} was not found in the list of tracks"
        return await interaction.response.send_message(embed=embed)

    if player and len(sql.check_player_server(player.id, interaction.guild_id)) != 1:
        embed.title = "player not found :("
        embed.description = f"{player.display_name} is not registered in the server"
        return await interaction.response.send_message(embed=embed)

    if player and not track:
        total = 0
        times = sql.get_player_best(mode=mode, guild_id=interaction.guild_id, player_id=player.id)
        embed.title = f"{player.display_name} {speed.name} {items.name}"
        embed.set_thumbnail(url=player.guild_avatar if player.guild_avatar else player.avatar)
        if len(times) == 0:
            embed.description = "No time to display sorry"
        else:
            for time in times:
                embed.description += f"**{time[0]}**: ``{time[1]}`` - {time[2]}/{time[3]}\n"
                total += int(time[1].split(':')[0])*60*1000 + int(time[1].split(':')[1].split('.')[0])*1000 + int(time[1].split(':')[1].split('.')[1])
            if len(times) == (len(sql.get_cups_emoji())*4):
                embed.add_field(name="total time", value=format_time(total))

    elif not player and not track:
        times = sql.get_best_times(mode=mode, guild_id=interaction.guild_id)
        embed.title = f"{speed.name} {items.name}"
        embed.set_thumbnail(url=interaction.guild.icon)
        if len(times) == 0:
            embed.description = "No time to display sorry"
        else:
            for time in times:
                member = interaction.guild.get_member(time[2])
                embed.description += f"**{time[0]}**: ``{time[1]}`` - {member.display_name}\n"

    elif not player and track:
        times = sql.get_track_times(mode=mode, guild_id=interaction.guild_id, track=track)
        if len(times) == 0:
            embed.title = f"{track} {speed.name} {items.name}"
            embed.description = "No time to display sorry"
        else:
            embed.title = f"{times[0][2]} {speed.name} {items.name}"
            embed.set_thumbnail(url=times[0][3])
            rank = 1
            for time in times:
                member = interaction.guild.get_member(time[0])
                embed.description += f"**{rank}:** {member.display_name} ``{time[1]}``\n"
                rank += 1

    else:
        times = sql.get_user_track_time(mode=mode, guild_id=interaction.guild_id, track=track, player_id=player.id)
        if len(times) == 0:
            embed.title = f"{player.display_name} {track} {speed.name} {items.name}"
            embed.description = "No time to display sorry"
        else:
            embed.title = f"{times[0][1]} {speed.name} {items.name}"
            embed.set_thumbnail(url=times[0][3])
            member = interaction.guild.get_member(times[0][0])
            embed.description = f"{member.display_name} - ``{times[0][2]}``"

    return await interaction.response.send_message(embed=embed)


async def setup(bot):
    bot.tree.add_command(display_time)