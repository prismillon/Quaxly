import discord
import aiohttp
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

from discord import app_commands
from autocomplete import name_autocomplete
from utils import lounge_season

def mmr_to_rank(mmr):
    if mmr < 2000:
        return "https://i.imgur.com/AYRMVEu.png", 0x817876 # Iron
    elif mmr < 4000:
        return "https://i.imgur.com/DxFLvtO.png", 0xE67E22 # Bronze
    elif mmr < 6000:
        return "https://i.imgur.com/xgFyiYa.png", 0x7D8396 # Silver
    elif mmr < 8000:
        return "https://i.imgur.com/6yAatOq.png", 0xF1C40F # Gold
    elif mmr < 10000:
        return "https://i.imgur.com/8v8IjHE.png", 0x3FABB8 # Platinum
    elif mmr < 12000:
        return "https://i.imgur.com/bXEfUSV.png", 0x286CD3 # Sapphire
    elif mmr < 14000:
        return "https://i.imgur.com/WU2NlJQ.png", 0xd41c60 # Ruby
    elif mmr < 16000:
        return "https://i.imgur.com/RDlvdvA.png", 0x9CCBD6 # Diamond
    elif mmr < 17000:
        return "https://i.imgur.com/3yBab63.png", 0x0E0B0B # Master
    else:
        return "https://i.imgur.com/EWXzu2U.png", 0xA3022C # Grand Master

def create_plot(base, history):
    ranks = [0, 2000, 4000, 6000, 8000, 10000, 12000, 14000, 16000, 17000]
    colors = ['#817876', '#E67E22', '#7D8396', '#F1C40F', '#3FABB8',
              '#286CD3', '#d41c60', '#9CCBD6', '#0E0B0B', '#A3022C']

    mmrhistory = [base]
    mmr = base
    for match in history:
        mmr += match
        mmrhistory.append(mmr)
    xs = np.arange(len(mmrhistory))
    plt.style.use('lounge_style.mplstyle')
    lines = plt.plot(mmrhistory)
    plt.setp(lines, 'color', 'snow', 'linewidth', 1.0)
    xmin, xmax, ymin, ymax = plt.axis()
    plt.xlabel("Matches played")
    plt.ylabel("MMR")
    plt.grid(True, 'both', 'both', color='snow', linestyle=':')

    for i in range(len(ranks)):
        if ranks[i] > ymax:
            continue
        maxfill = ymax
        if i + 1 < len(ranks):
            if ranks[i] < ymin and ranks[i+1] < ymin:
                continue
            if ranks[i+1] < ymax:
                maxfill = ranks[i+1]
        if ranks[i] < ymin:
            minfill = ymin
        else:
            minfill = ranks[i]
        plt.fill_between(xs, minfill, maxfill, color=colors[i])
    plt.fill_between(xs, ymin, mmrhistory, color='#212121')
    b = BytesIO()
    plt.savefig(b, format='png', bbox_inches='tight')
    b.seek(0)
    plt.close()
    return b

@app_commands.command()
@app_commands.autocomplete(player=name_autocomplete)
@app_commands.describe(player="The player you want to check lounge profile from")
async def lounge_profile(interaction: discord.Interaction, player: str = None):
    """lounge profile of a player"""

    await interaction.response.defer()

    embed = discord.Embed(color=0x47e0ff)


    scores = []
    parteners_scores = []
    seasons = {}
    season_played = []
    for i in range(4, lounge_season.data()+1):
        seasons[i] = {}

    async with aiohttp.ClientSession() as session:
        if not player:
            async with session.get("https://www.mk8dx-lounge.com/api/player?discordId="+str(interaction.user.id)) as response:
                if response.status == 200:
                    user_data = await response.json()
                    player = user_data['name']
                else:
                    return await interaction.followup.send(content="could not found your account in the lounge", ephemeral=True)
        for season in seasons:
            async with session.get("https://www.mk8dx-lounge.com/api/player/details?name="+player+"&season="+str(season)) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data['mmrChanges']:
                        seasons[season] = None
                        continue
                    seasons[season]['base'] = data['mmrChanges'][-1]['newMmr']
                    seasons[season]['endingMmr'] = data['mmr']

                    if len(data['mmrChanges']) > 1:
                        season_played.append(season)
                    seasons[season]['rank'] = data['rank']
                    season_history = []
                    for match in data['mmrChanges'][::-1]:
                        season_history.append(match['mmrDelta'])
                        if match['reason'] == 'Table':
                            scores.append(match['score'])
                            parteners_scores += match['partnerScores']
                    seasons[season]['history'] = season_history
                else:
                    return await interaction.followup.send(content="player not found", ephemeral=True)
    if len(scores) == 0:
        return await interaction.followup.send(content="player has not played yet", ephemeral=True)
    embed.title = f"{player}'s profile"
    embed.add_field(name="avg score", value=str(round(sum(scores)/len(scores), 2)), inline=True)
    embed.add_field(name="partner avg", value=str(round(sum(parteners_scores)/len(parteners_scores), 2)), inline=True)
    embed.add_field(name="events played", value=str(len(scores)), inline=True)
    embed.add_field(name="seasons played", value=str(season_played)[1:-1], inline=True)
    embed.set_thumbnail(url=mmr_to_rank(seasons[season_played[-1]]['endingMmr'])[0])
    embed.color = mmr_to_rank(seasons[season_played[-1]]['endingMmr'])[1]

    base = 0
    for season in seasons:
        if seasons[season]:
            base = seasons[season]['base']
            break
    history = []
    for season in seasons:
        if seasons[season]:
            if len(history) > 0:
                history.append(seasons[season]['base'] - seasons[season-1]['endingMmr'])
            history += seasons[season]['history']
    embed.set_image(url="attachment://plot.png")
    if base != 0 and len(history) > 0:
        return await interaction.followup.send(embed=embed, file=discord.File(create_plot(base, history), "plot.png"))
    return await interaction.followup.send(content="player not found", ephemeral=True)


async def setup(bot):
    bot.tree.add_command(lounge_profile)