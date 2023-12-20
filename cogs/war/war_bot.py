import re

from datetime import datetime, timedelta
from discord.ext import commands, tasks
from discord import app_commands

import discord
import sql

from cogs.war.base import Base
from autocomplete import mkc_team_autocomplete
from utils import mkc_data

_SCORE = (15, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)

def text_to_score(text: str):
    data = []
    prev = None
    next_list = []
    loopFlag = False
    while text:
        next_list = []
        if text.startswith('-'):
            loopFlag = True
            text = text[1:]
            if data:
                prev = data[-1]
            else:
                prev = 0
        if text.startswith('0'):
            next_list = [10]
            text = text[1:]
        elif text.startswith('+'):
            next_list = [11]
            text = text[1:]
        elif text.startswith('10'):
            next_list = [10]
            text = text[2:]
        elif text.startswith('110'):
            next_list = [1, 10]
            text = text[3:]
        elif text.startswith('1112'):
            next_list = [11, 12]
            text = text[4:]
        elif text.startswith('111'):
            next_list = [1, 11]
            text = text[3:]
        elif text.startswith('112'):
            next_list = [1, 12]
            text = text[3:]
        elif text.startswith('11'):
            next_list = [11]
            text = text[2:]
        elif text.startswith('12'):
            if data:
                next_list = [12]
            else:
                next_list = [1, 2]
            text = text[2:]
        elif text:
            next_list = [int(text[0], 16)]
            text = text[1:]
        if loopFlag:
            if not next_list:
                next_list = [12]
            next = next_list[0]
            while next - prev > 1:
                data.append(prev+1)
                prev += 1
            loopFlag = False
        data += next_list
    return validate_score(set(data))

def validate_score(data: (int)):
    last_spot = 12
    while len(data) < 6:
        data.add(last_spot)
        last_spot -= 1
    return sorted(list(data))[:6]

def make_embed(war):
    embed = discord.Embed(color=0x47e0ff, title=f"Total Score after Race {len(war['diff'])}")
    diff = sum(war['home_score']) - sum(war['ennemy_score'])
    embed.add_field(name=war['tag'], value=sum(war['home_score']))
    embed.add_field(name=war['ennemy_tag'], value=sum(war['ennemy_score']))
    embed.add_field(name="Difference", value=f"{diff if diff < 0 else '+' + str(diff)}", inline=False)
    if len(war['diff']) > 0:
        race_field_value = "```\n"
        for i, (spot, diff, track) in enumerate(zip(war['spots'], war['diff'], war['tracks'])):
            diff = str(diff) if diff<0 else '+'+str(diff)
            spot = re.sub('[\[\] ]', '', str(spot))
            race_field_value += f"{i + 1 if i + 1 > 9 else ' '+str(i + 1)}: {diff if len(diff) == 3 else ' ' + diff} | {spot} {'(' + track[1] + ')' if len(track) != 1 else ''}\n"
        race_field_value += "```"
        embed.add_field(name="Races", value=race_field_value, inline=False)
    return embed

class WarBot(Base):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_war = {}
        self._remove_war_task = self.remove_expired_war.start()

    @app_commands.command(name="start")
    @app_commands.guild_only()
    @app_commands.autocomplete(tag=mkc_team_autocomplete, ennemy_tag=mkc_team_autocomplete)
    @app_commands.describe(tag="the tag of your team", ennemy_tag="the tag of the ennemie team")
    async def warstart(self, interaction: discord.Interaction, tag: str, ennemy_tag: str):
        """start a war in the channel"""

        tag = next(filter(lambda team: team['team_name'] == tag, mkc_data.data()))['team_tag']
        ennemy_tag = next(filter(lambda team: team['team_name'] == ennemy_tag, mkc_data.data()))['team_tag']

        date = datetime.utcnow()
        await sql.new_war(interaction.channel.id, date, tag, ennemy_tag)
        self.active_war[interaction.channel.id] = {
            "war_id": (await sql.check_war_id(interaction.channel.id, date, tag, ennemy_tag))[0][0],
            "date": date,
            "tag": tag,
            "ennemy_tag": ennemy_tag,
            "home_score": [],
            "ennemy_score": [],
            "spots": [],
            "diff": [],
            "tracks": [],
            "incomming_track": ()
        }
        return await interaction.response.send_message(f"started war between {tag} and {ennemy_tag}")


    @app_commands.command(name="stop")
    @app_commands.guild_only()
    async def warstop(self, interaction: discord.Interaction):
        """stop the war"""

        if self.active_war[interaction.channel.id]:
            if len(await sql.check_war_length(self.active_war[interaction.channel.id]['war_id'])) < 2:
                await sql.delete_races_from_war(self.active_war[interaction.channel.id]['war_id'])
                await sql.delete_war(self.active_war[interaction.channel.id]['war_id'])
            self.active_war.pop(interaction.channel.id)
            return await interaction.response.send_message("stopped war")
        await interaction.response.send_message("no active war")


    @tasks.loop(minutes=1)
    async def remove_expired_war(self):
        expired_date = datetime.now()-timedelta(hours=3)
        for channel_id, data in list(self.active_war.items()):
            if data['date'] < expired_date:
                self.active_war.pop(channel_id)


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id not in self.active_war or message.content == '':
            return

        war = self.active_war[message.channel.id]

        if message.content.startswith('race '):
            data = message.content.split(' ')
            if not data[1].isnumeric() or len(data) != 3:
                return
            track = await sql.get_track_details(data[2])
            if len(track) != 1:
                return
            track = track[0]
            war['tracks'][int(data[1])-1] = track[4], track[1]
            await sql.update_this_race_track(data[1], war['war_id'], track[4])
            self.active_war[message.channel.id] = war
            return await message.reply(embed=make_embed(war), mention_author=False)

        if ' ' in message.content:
            return

        if message.content.lower() == 'back':
            race_id = len(war["spots"])
            await sql.delete_this_race(race_id, war["war_id"])
            war['spots'] = war['spots'][:race_id-1]
            war['diff'] = war['diff'][:race_id-1]
            war['tracks'] = war['tracks'][:race_id-1]
            war['home_score'] = war['home_score'][:race_id-1]
            war['ennemy_score'] = war['ennemy_score'][:race_id-1]
            self.active_war[message.channel.id] = war
            return await message.reply(embed=make_embed(war), mention_author=False)

        if re.fullmatch("^((?!--)[0-9\+\-])+$", message.content):
            spots = text_to_score(message.content)
            scored = sum(map(lambda r: _SCORE[r-1], spots))
            war['spots'].append(spots)
            war['home_score'].append(scored)
            war['ennemy_score'].append(82-scored)
            war['diff'].append(war['home_score'][-1] - war['ennemy_score'][-1])
            war['tracks'].append(war['incomming_track'] or ["NULL"])
            war['incomming_track'] = ()
            await sql.new_race(len(war["spots"]), war['war_id'], war['tracks'][-1][0], war['diff'][-1], war['spots'][-1])
            self.active_war[message.channel.id] = war
            return await message.reply(embed=make_embed(war), mention_author=False)

        track = await sql.get_track_details(message.content)

        if len(track) == 1:
            track = track[0]
            war['incomming_track'] = track[4], track[1]
            return await message.reply(embed=discord.Embed(color=0x47e0ff,title=f"{track[1]} | {track[4]}").set_image(url=f"http://japan-mk.blog.jp/mk8dx.info-4/table/{track[0]:02d}.jpg"), mention_author=False)
