import discord
import aiohttp
import asyncio
import statistics
import re


from autocomplete import mkc_team_autocomplete
from datetime import datetime
from discord import app_commands
from utils import lounge_data, statChoices, mkc_data, wait_for_chunk, lounge_season
from discord.app_commands import Choice, Range


async def check_for_none(data: list) -> bool:
    for item in data:
        if item is not None:
            return True
    return False


async def id_to_stat(discord_id: int, stat: Choice[str] = statChoices[0], season: int = None):
    season = f"&season={season}" if season else ""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.mk8dx-lounge.com/api/player?discordId="+str(discord_id)+season) as response:
            if response.status == 200:
                user_data = await response.json()
                if "discordId" not in user_data:
                    return None
                if stat.value == 'eventsPlayed':
                    async with session.get("https://www.mk8dx-lounge.com/api/player/details?name="+user_data['name']+season) as response:
                        if response.status == 200:
                            user_data = await response.json()
                            user_data['discordId'] = discord_id
                            user_data['id'] = user_data['playerId']
                if 'mmr' not in user_data:
                    return None
                if 'maxMmr' not in user_data:
                    user_data['maxMmr'] = user_data['mmr']
                return user_data


async def fc_to_stat(fc: str, season: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://www.mk8dx-lounge.com/api/player/leaderboard?season={season}&search=switch="+fc) as response:
            if response.status == 200:
                user_data = await response.json()
                if len(user_data['data']) != 1:
                    return None
                user_data = user_data['data'][0]
                user_data['discordId'] = next((player['discordId'] for player in lounge_data.data() if player['name'] == user_data['name']), None)
                if not 'discordId' in user_data:
                    return None
                if 'mmr' not in user_data or not 'discordId' in user_data:
                    return None
                if 'maxMmr' not in user_data:
                    user_data['maxMmr'] = user_data['mmr']
                return user_data


@app_commands.command()
@app_commands.guild_only()
@app_commands.choices(stat=statChoices)
@app_commands.describe(role="the role you want to check stats from", stat="the type of stats", season="the season you want this info from")
async def role_stats(interaction: discord.Interaction, role: discord.Role, stat: Choice[str] = None, season: int = None):
    """check stats of a discord role"""

    if not interaction.guild.chunked:
        return await wait_for_chunk(interaction)

    await interaction.response.defer()

    if not stat:
        stat = statChoices[0]

    embeds = [discord.Embed(color=0x47e0ff, title=f"{role.name} average {stat.name}")]

    member_tasks = [id_to_stat(member.id, stat=stat, season=season) for member in role.members]
    user_data_array = sorted(list(filter(lambda user_data: user_data is not None, await asyncio.gather(*member_tasks))), key=lambda key: key[stat.value], reverse=True)

    if len(user_data_array) == 0:
        return await interaction.edit_original_response(embed=discord.Embed(color=0x47e0ff, title=f"no users found", description="could not find anyone in lounge from this role"))

    for index, user in enumerate(user_data_array):
        if index%21==0 and index != 0:
            embeds.append(discord.Embed(color=0x47e0ff))
        embeds[-1].add_field(name=user['name'], value=f"<@{user['discordId']}> ([{user[stat.value]}](https://www.mk8dx-lounge.com/PlayerDetails/{user['id']}))")

    if len(embeds)>10:
        return await interaction.edit_original_response(embed=discord.Embed(color=0x47e0ff, title=f"too many users", description="too many users in this role, please select less people"))

    embeds[-1].add_field(name='\u200B', value='\u200B', inline=False)
    embeds[-1].add_field(name='average', value=f"__{round(statistics.fmean([user[stat.value] for user in user_data_array]))}__")
    embeds[-1].add_field(name='top 6', value=f"__{round(statistics.fmean([user[stat.value] for user in user_data_array][:6]))}__")

    await interaction.edit_original_response(embeds=embeds)


@app_commands.command()
@app_commands.autocomplete(team=mkc_team_autocomplete)
@app_commands.choices(stat=statChoices)
@app_commands.describe(team="the team you want to check stats from", stat="the type of stats", season="the season you want this info from")
async def mkc_stats(interaction: discord.Interaction, team: str, stat: Choice[str] = None, season: int = None):
    """check stats of a mkc 150cc team"""

    if not season:
        season = lounge_season.data()

    if not mkc_data.data():
        await interaction.response.send_message(content="mario kart central api is not loaded yet, please retry in a few seconds", ephemeral=True)

    await interaction.response.defer()

    team = next((mkc_team for mkc_team in mkc_data.data() if mkc_team['team_name'].lower() == team.lower()), None)

    if not team:
        return await interaction.edit_original_response(embed=discord.Embed(color=0x47e0ff, title=f"team not found", description="could not find the team you typed in the mkc database"))

    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.mariokartcentral.com/mkc/api/registry/teams/"+str(team['team_id'])) as response:
            if response.status == 200:
                team_data = await response.json()
    
    if not team_data or not team_data['rosters']['150cc']:
        return await interaction.edit_original_response(embed=discord.Embed(color=0x47e0ff, title=f"team not found", description="could not find the team you typed in the mkc 150cc database"))

    if not stat:
        stat = statChoices[0]

    embeds = [discord.Embed(color=0x47e0ff, title=f"{team['team_name']} average {stat.name}").set_thumbnail(url=f"https://www.mariokartcentral.com/mkc/storage/{team_data['team_logo']}")]

    member_tasks = [fc_to_stat(member['custom_field'], season=season) for member in team_data['rosters']['150cc']['members']]
    user_data_array = sorted(list(filter(lambda user_data: user_data is not None, await asyncio.gather(*member_tasks))), key=lambda key: key[stat.value], reverse=True)

    if len(user_data_array) == 0:
        return await interaction.edit_original_response(embed=discord.Embed(color=0x47e0ff, title=f"no users found", description="could not find anyone in lounge from this team"))

    for index, user in enumerate(user_data_array):
        if index%21==0 and index != 0:
            embeds.append(discord.Embed(color=0x47e0ff))
        embeds[-1].add_field(name=user['name'], value=f"<@{user['discordId']}> ([{user[stat.value]}](https://www.mk8dx-lounge.com/PlayerDetails/{user['id']}))")

    if len(embeds)>10:
        return await interaction.edit_original_response(embed=discord.Embed(color=0x47e0ff, title=f"too many users", description="too many users in this role, please select less people"))

    embeds[-1].add_field(name='\u200B', value='\u200B', inline=False)
    embeds[-1].add_field(name='average', value=f"__{round(statistics.fmean([user[stat.value] for user in user_data_array]))}__")
    embeds[-1].add_field(name='top 6', value=f"__{round(statistics.fmean([user[stat.value] for user in user_data_array][:6]))}__")

    await interaction.edit_original_response(embeds=embeds)


@app_commands.command()
@app_commands.describe(room="room message with the list of fc", team_size="the size of the team for this summit")
async def summit_stats(interaction: discord.Interaction, room: str, team_size: Range[int, 1, 6] = 1):
    """get stats from summit room"""

    if len(re.findall("[0-9]{4}-[0-9]{4}-[0-9]{4}", room)) != 12:
        return await interaction.response.send_message(content="room list provided is not valid", ephemeral=True)

    await interaction.response.defer()

    season = lounge_season.data()
    players_fc = re.findall("[0-9]{4}-[0-9]{4}-[0-9]{4}", room)
    players_api_request = [fc_to_stat(fc, season) for fc in players_fc]
    players_profile = await asyncio.gather(*players_api_request)
    teams = []

    for index, profile in enumerate(players_profile):
        if index%team_size==0:
            teams.append([])
        teams[-1].append(profile)

    embed = discord.Embed(color=0x47e0ff, title=f"room average {round(statistics.fmean([user['mmr'] for user in filter(lambda x: x is not None, players_profile)]))}")

    for index, team in enumerate(teams):
        title = f"team {index+1}: "
        if await check_for_none(team):
            title += f"{round(statistics.fmean([user['mmr'] for user in filter(lambda x: x is not None, team)]))}"
        else:
            title += 'N/A'
        value = ""
        for member in team:
            value += f"[{member['name']}](https://www.mk8dx-lounge.com/PlayerDetails/{member['id']}): {member['mmr']}\n" if member else "not in lounge\n"
        embed.add_field(name=title, value=value, inline=False)

    await interaction.followup.send(embed=embed)


async def setup(bot):
    bot.tree.add_command(summit_stats)
    bot.tree.add_command(role_stats)
    bot.tree.add_command(mkc_stats)
