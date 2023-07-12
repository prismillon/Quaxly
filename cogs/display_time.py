import discord
import utils
import sql

from discord import app_commands
from discord.app_commands import Choice
from autocomplete import track_autocomplete


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(speed="the mode you want to display", items="do you want to only display times with shrooms or without?", track="the track you want to display", player="the player you want to display")
@app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
@app_commands.autocomplete(track=track_autocomplete)
async def display_time(ctx: discord.Interaction, speed: Choice[str], items: Choice[str], track: str = None, player: discord.Member = None):
    """display a specific time, a category or even all times"""

    if not ctx.guild.chunked:
        ctx.guild.chunk()

    mode = items.value+speed.value
    embed = discord.Embed(color=0x47e0ff, description="")
    
    if mode not in utils.allowed_tables:
        return await ctx.response.send_message(content=":euh:")

    if track and len(sql.check_track_name(track)) != 1:
        embed.title = "track not found :("
        embed.description = f"{track} was not found in the list of tracks"
        return await ctx.response.send_message(embed=embed)

    if player and len(sql.check_player_server(player.id, ctx.guild_id)) != 1:
        embed.title = "player not found :("
        embed.description = f"{player.display_name} is not registered in the server"
        return await ctx.response.send_message(embed=embed)

    if player and not track:
        times = sql.get_player_best(mode=mode, guild_id=ctx.guild_id, player_id=player.id)
        embed.title = f"{player.display_name} {speed.name} {items.name}"
        embed.set_thumbnail(url=player.guild_avatar if player.guild_avatar else player.avatar)
        if len(times) == 0:
            embed.description = "No time to display sorry"
        else:
            for time in times:
                embed.description += f"**{time[0]}**: ``{time[1]}`` - {time[2]}/{time[3]}\n"

    elif not player and not track:
        times = sql.get_best_times(mode=mode, guild_id=ctx.guild_id)
        embed.title = f"{speed.name} {items.name}"
        embed.set_thumbnail(url=ctx.guild.icon)
        if len(times) == 0:
            embed.description = "No time to display sorry"
        else:
            for time in times:
                member = ctx.guild.get_member(time[2])
                embed.description += f"**{time[0]}**: ``{time[1]}`` - {member.display_name}\n"

    elif not player and track:
        times = sql.get_track_times(mode=mode, guild_id=ctx.guild_id, track=track)
        if len(times) == 0:
            embed.title = f"{track} {speed.name} {items.name}"
            embed.description = "No time to display sorry"
        else:
            embed.title = f"{times[0][2]} {speed.name} {items.name}"
            embed.set_thumbnail(url=times[0][3])
            rank = 1
            for time in times:
                member = ctx.guild.get_member(time[0])
                embed.description += f"**{rank}:** {member.display_name} ``{time[1]}``\n"
                rank += 1

    else:
        times = sql.get_user_track_time(mode=mode, guild_id=ctx.guild_id, track=track, player_id=player.id)
        if len(times) == 0:
            embed.title = f"{player.display_name} {track} {speed.name} {items.name}"
            embed.description = "No time to display sorry"
        else:
            embed.title = f"{times[0][1]} {speed.name} {items.name}"
            embed.set_thumbnail(url=times[0][3])
            member = ctx.guild.get_member(times[0][0])
            embed.description = f"{member.display_name} - ``{times[0][2]}``"

    return await ctx.response.send_message(embed=embed)
