import discord
import aiohttp
import asyncio
import statistics


from autocomplete import mkc_team_autocomplete
from datetime import datetime
from discord import app_commands
from utils import lounge_data, statChoices, mkc_data, wait_for_chunk
from discord.app_commands import Choice


async def id_to_stat(discord_id: int, stat: Choice[str], season: int):
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


async def fc_to_stat(fc: str, stat: Choice[str], season: int):
    season = f"&season={season}" if season else ""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.mk8dx-lounge.com/api/player?fc="+fc+season) as response:
            if response.status == 200:
                user_data = await response.json()
                if "discordId" not in user_data:
                    return None
                if stat.value == 'eventsPlayed':
                    async with session.get("https://www.mk8dx-lounge.com/api/player/details?name="+user_data['name']+season) as response:
                        if response.status == 200:
                            discord_id = user_data['discordId']
                            user_data = await response.json()
                            user_data['discordId'] = discord_id
                            user_data['id'] = user_data['playerId']
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

    member_tasks = [fc_to_stat(member['custom_field'], stat=stat, season=season) for member in team_data['rosters']['150cc']['members']]
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


async def setup(bot):
    bot.tree.add_command(role_stats)
    bot.tree.add_command(mkc_stats)
