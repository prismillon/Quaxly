import discord
import sql
import re

from cogs.war.base import Base
from discord import app_commands
from discord.ext import commands, tasks
from typing import Optional
from datetime import datetime, timedelta
from discord.app_commands import Choice
from autocomplete import mkc_team_autocomplete

_score = (15, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)

def text_to_score(text: str):
    data = []
    prev = 1
    if text[0] == '-':
        data.append(prev)
        prev = '-'
        text = text[1:]
    for value in text:
        if prev == '-':
            if value == '+':
                value = 11
            elif value == '0':
                value = 10
            data += range(data[-1]+1, int(value)+1)
        elif value == '-':
            prev = value
            continue
        elif value == '0':
            data.append(10)
        elif value == '+':
            data.append(11)
        else:
            data.append(int(value))
        prev = value
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
    embed.add_field(name=f"{war['tag']} - {war['ennemy_tag']}", value=f"`{sum(war['home_score'])} - {sum(war['ennemy_score'])}` | `{diff if diff < 0 else '+' + str(diff)}`")
    if len(war['diff']) > 0:
        for i, (h_score, e_score, spot, diff, track) in enumerate(zip(war['home_score'], war['ennemy_score'], war['spots'], war['diff'], war['tracks'])):
            embed.add_field(name=f"{i+1} {'| '+track[1]+' | '+track[0] if len(track) != 1 else ''}", value=f"`{h_score} : {e_score} ({diff if diff<0 else '+'+str(diff)})` | `{spot}`", inline=False)
    return embed

class war_bot(Base):
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

        date = datetime.utcnow()
        sql.new_war(interaction.channel.id, date, tag, ennemy_tag)
        self.active_war[interaction.channel.id] = {
            "war_id": sql.check_war_id(interaction.channel.id, date, tag, ennemy_tag)[0][0],
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
            if len(sql.check_war_length(self.active_war[interaction.channel.id]['war_id'])) < 2:
                sql.delete_races_from_war(self.active_war[interaction.channel.id]['war_id'])
                sql.delete_war(self.active_war[interaction.channel.id]['war_id'])
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
            track = sql.get_track_details(data[2])
            if len(track) != 1:
                return
            track = track[0]
            war['tracks'][int(data[1])-1] = track[4], track[1]
            sql.update_this_race_track(data[1], war['war_id'], track[4])
            self.active_war[message.channel.id] = war
            return await message.reply(embed=make_embed(war), mention_author=False)
        
        if ' ' in message.content:
            return

        if message.content.lower() == 'back':
            race_id = len(war["spots"])
            sql.delete_this_race(race_id, war["war_id"])
            war['spots'] = war['spots'][:race_id-1]
            war['diff'] = war['diff'][:race_id-1]
            war['tracks'] = war['tracks'][:race_id-1]
            war['home_score'] = war['home_score'][:race_id-1]
            war['ennemy_score'] = war['ennemy_score'][:race_id-1]
            self.active_war[message.channel.id] = war
            return await message.reply(embed=make_embed(war), mention_author=False)

        if re.fullmatch("[0-9\+\-]+", message.content):
            spots = text_to_score(message.content)
            scored = sum(map(lambda r: _score[r-1], spots))
            war['spots'].append(spots)
            war['home_score'].append(scored)
            war['ennemy_score'].append(82-scored)
            war['diff'].append(war['home_score'][-1] - war['ennemy_score'][-1])
            war['tracks'].append(war['incomming_track'] or ["NULL"])
            war['incomming_track'] = ()
            sql.new_race(len(war["spots"]), war['war_id'], war['tracks'][-1][0], war['diff'][-1], war['spots'][-1])
            self.active_war[message.channel.id] = war
            return await message.reply(embed=make_embed(war), mention_author=False)

        track = sql.get_track_details(message.content)

        if len(track) == 1:
            track = track[0]
            war['incomming_track'] = track[4], track[1]
            return await message.reply(embed=discord.Embed(color=0x47e0ff,title=f"{track[1]} | {track[4]}").set_image(url=f"http://japan-mk.blog.jp/mk8dx.info-4/table/{track[0]:02d}.jpg"), mention_author=False)
            