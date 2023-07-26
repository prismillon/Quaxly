import discord
import sql

from discord import app_commands
from discord.ext import commands
from datetime import datetime


class war_stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_war = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.id == 177162177432649728:
            return

        if "Started MK8DX 6v6" in message.content:
            extract_tag = message.content.replace("Started MK8DX 6v6: ", '')
            extract_tag = extract_tag[:-1].split(" vs ")
            tag = extract_tag[0]
            ennemy_tag = extract_tag[1]
            date = datetime.utcnow()
            sql.new_war(message.channel.id, date, tag, ennemy_tag)
            self.active_war[message.channel.id] = {
                "war_id": sql.check_war_id(message.channel.id, date, tag, ennemy_tag)[0][0],
                "date": date,
                "tag": tag,
                "ennemy_tag": ennemy_tag,
                "spots": [],
                "diff": [],
                "tracks": []
            }
            return

        if message.channel.id in self.active_war:

            if "Stopped war." in message.content:
                if len(sql.check_war_length(self.active_war[message.channel.id]['war_id'])) < 2:
                    sql.delete_races_from_war(self.active_war[message.channel.id]['war_id'])
                    sql.delete_war(self.active_war[message.channel.id]['war_id'])
                self.active_war.pop(message.channel.id)
                return

            if len(message.embeds) >= 1:
                race_data = message.embeds[0].to_dict()

                if "Score for Race" in race_data['title']:
                    spots = sorted([int(spot[:-2]) for spot in race_data['fields'][0]['value'].split(", ")])
                    track = race_data['fields'][4]['value'] if len(race_data['fields']) == 5 else "NULL"
                    diff = race_data['fields'][3]['value']
                    race_id = race_data['title'].replace("Score for Race ", '')
                    sql.new_race(race_id, self.active_war[message.channel.id]['war_id'], track, diff, spots)
                    self.active_war[message.channel.id]['spots'].append(spots)
                    self.active_war[message.channel.id]['diff'].append(diff)
                    self.active_war[message.channel.id]['tracks'].append(track)
                    return

                if "Total Score after Race" in race_data['title']:
                    race_id = int(race_data['title'].replace("Total Score after Race ", ''))
                    for race in range(race_id, len(self.active_war[message.channel.id]['diff'])):
                        sql.delete_this_race(race+1, self.active_war[message.channel.id]['war_id'])
                    self.active_war[message.channel.id]['spots'] = self.active_war[message.channel.id]['spots'][:race_id]
                    self.active_war[message.channel.id]['diff'] = self.active_war[message.channel.id]['diff'][:race_id]
                    self.active_war[message.channel.id]['tracks'] = self.active_war[message.channel.id]['tracks'][:race_id]
                    return


async def setup(bot: commands.Bot):
    await bot.add_cog(war_stats(bot))
