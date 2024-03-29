from datetime import datetime
import discord

from discord import app_commands
from discord.ext import commands

import utils
import sql

from utils import ConfirmButton
from cogs.war.base import Base
from autocomplete import track_autocomplete


formatNumber = lambda n: n if n%1 else int(n)

class WarStats(Base):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_toad_war = {}

    @commands.Cog.listener(name="on_message")
    async def toad_tracking(self, message: discord.Message):
        if message.author.id != 177162177432649728:
            return

        if "Started MK8DX 6v6" in message.content:
            extract_tag = message.content.replace("Started MK8DX 6v6: ", '')
            extract_tag = extract_tag[:-1].split(" vs ")
            tag = extract_tag[0]
            ennemy_tag = extract_tag[1]
            date = datetime.utcnow()
            await sql.new_war(message.channel.id, date, tag, ennemy_tag)
            self.active_toad_war[message.channel.id] = {
                "war_id":(await sql.check_war_id(message.channel.id, date, tag, ennemy_tag))[0][0],
                "date": date,
                "tag": tag,
                "ennemy_tag": ennemy_tag,
                "spots": [],
                "diff": [],
                "tracks": []
            }
            return

        if message.channel.id not in self.active_toad_war:
            return

        if "Stopped war." in message.content:
            if len(await sql.check_war_length(self.active_toad_war[message.channel.id]['war_id'])) < 2:
                await sql.delete_races_from_war(self.active_toad_war[message.channel.id]['war_id'])
                await sql.delete_war(self.active_toad_war[message.channel.id]['war_id'])
            self.active_toad_war.pop(message.channel.id)
            return

        if len(message.embeds) == 0:
            return

        race_data = message.embeds[0].to_dict()

        if "Score for Race" in race_data['title']:
            spots = sorted([int(spot[:-2]) for spot in race_data['fields'][0]['value'].split(", ")])
            track = race_data['fields'][4]['value'] if len(race_data['fields']) == 5 else "NULL"
            diff = race_data['fields'][3]['value']
            race_id = race_data['title'].replace("Score for Race ", '')
            await sql.new_race(race_id, self.active_toad_war[message.channel.id]['war_id'], track, diff, spots)
            self.active_toad_war[message.channel.id]['spots'].append(spots)
            self.active_toad_war[message.channel.id]['diff'].append(diff)
            self.active_toad_war[message.channel.id]['tracks'].append(track)

        elif "Total Score after Race" in race_data['title']:
            race_id = int(race_data['title'].replace("Total Score after Race ", ''))
            for race in range(race_id, len(self.active_toad_war[message.channel.id]['diff'])):
                await sql.delete_this_race(race+1, self.active_toad_war[message.channel.id]['war_id'])
            self.active_toad_war[message.channel.id]['spots'] = self.active_toad_war[message.channel.id]['spots'][:race_id]
            self.active_toad_war[message.channel.id]['diff'] = self.active_toad_war[message.channel.id]['diff'][:race_id]
            self.active_toad_war[message.channel.id]['tracks'] = self.active_toad_war[message.channel.id]['tracks'][:race_id]


    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(channel="the channel you want to check stats from", minimum="the minimum number of times the track has been played for it to count", track="the track you want to check stats from")
    @app_commands.autocomplete(track=track_autocomplete)
    async def stats(self, interaction: discord.Interaction, channel: discord.TextChannel = None, minimum: app_commands.Range[int, 1] = 1, track: str = None) -> None:
        """check race stats in the specified channel"""

        channel = channel or interaction.channel

        raw_stats = list(filter(lambda x: x[1] >= minimum, await sql.get_wars_stats_from_channel(channel.id)))

        if track:
            raw_stats = list(filter(lambda x: x[3] == track, raw_stats))
            if len(raw_stats) == 0:
                return await interaction.response.send_message(content=f"no stats registered in this channel for the track {track}", ephemeral=True)
            embed = discord.Embed(color=0x47e0ff, description=f"stats for {track}:\n\n```{raw_stats[0][3]} | {raw_stats[0][2]} | {raw_stats[0][1]}```")
            return await interaction.response.send_message(embed=embed)

        if len(raw_stats) == 0:
            return await interaction.response.send_message(content="no stats registered in this channel", ephemeral=True)
        
        max_name_l = len(max(raw_stats, key=lambda x: len(x[3]))[3])+1
        max_diff = str(max(raw_stats, key=lambda x: len(str(x[2])) if float(x[2])<0 else len(str(x[2]))+1)[2])
        max_diff_l = len(max_diff)+1 if float(max_diff)<0 else len(max_diff)+2
        stats = [f"```{stat[3]}{' '*(max_name_l-len(stat[3]))}{stat[2]:+g}{' '*(max_diff_l-(len(str(formatNumber(stat[2]))) if stat[2]<0 else len(str(formatNumber(stat[2])))+1))} | {stat[1]}```" for stat in raw_stats]
        
        embeds = []

        for index, stat in enumerate(stats):
            if index%10==0:
                embeds.append(discord.Embed(color=0x47e0ff, description="", title=f"race stats [ {index+1} -> {index+10 if len(stats)>=index+10 else len(stats)} ]"))
            embeds[-1].description += stat

        await interaction.response.send_message(embed=embeds[0], view=utils.Paginator(interaction, embeds))


    @app_commands.command(name="list")
    @app_commands.guild_only()
    @app_commands.describe(channel="the channel you want to check wars from")
    async def warlist(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """check the list of war that have been recorded"""

        channel = channel or interaction.channel
        
        raw_stats = await sql.get_war_list_from_channel(channel.id)

        if len(raw_stats) == 0:
            return await interaction.response.send_message(content="no wars registered in this channel", ephemeral=True)

        embeds = []

        for war in raw_stats:
            embed = discord.Embed(color=0x47e0ff, title=f"{war[3]} vs {war[4]}", timestamp=datetime.fromisoformat(war[2]))
            races = await sql.get_races_from_war(war[0])
            if len(races) == 0:
                continue
            embed.add_field(name="final result", value=f"```{sum(race[3] for race in races):+}```", inline=True)
            embed.add_field(name="war id", value=f"```{war[0]}```", inline=True)
            race_text = "```\n"
            max_name_l = len(max(races, key=lambda x: len(x[2]))[2])+1
            for index, race in enumerate(races):
                if index == 20:
                    race_text += "[...]\n"
                    break
                race_text += f"{race[0]}:{' ' if len(str(race[0]))==1 else ''} {race[2]}{' '*(max_name_l-len(race[2]))} {' ' if abs(race[3])<10 else ''}{race[3]:+}\n"
            embed.add_field(name="race list", value=f"{race_text}```", inline=False)
            embeds.append(embed)

        if len(embeds) == 0:
            return await interaction.response.send_message(content="no wars to display in this channel", ephemeral=True)

        await interaction.response.send_message(embed=embeds[0], view=utils.Paginator(interaction, embeds))


    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe()
    async def delete(self, interaction: discord.Interaction, channel: discord.TextChannel = None, war_id: app_commands.Range[int, 1] = None):
        """delete stats from a specific war or all stats"""


        channel = channel or interaction.channel

        if not war_id:
            if len(await sql.get_war_list_from_channel(channel.id)) == 0:
                return await interaction.response.send_message(content="this channel do not have any war stats", ephemeral=True)

            embed = discord.Embed(color=0x47e0ff, title="delete all war stats")
            embed.description = f"you are about to delete {len(await sql.get_war_list_from_channel(channel.id))} wars"
            view = ConfirmButton()
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            await view.wait()

            if view.answer:
                for war in await sql.get_war_list_from_channel(channel.id):
                    await sql.delete_races_from_war(war[0])
                    await sql.delete_war(war[0])
                embed.title = "war stats removed"
                embed.description = "all war stats have been removed"

            else:
                embed.title = "action canceled"
                embed.description = "data remained unchanged"
        
        else:
            war = await sql.check_war_ownership(war_id, channel.id)

            if len(war) != 1:
                return await interaction.response.send_message(content="this war does not exist or does not belong to this channel", ephemeral=True)

            embed = discord.Embed(color=0x47e0ff, title=f"delete war n°{war_id}")
            embed.description = "you are about to delete this wars"
            view = ConfirmButton()

            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            await view.wait()

            if view.answer:
                await sql.delete_races_from_war(war_id)
                await sql.delete_war(war_id)
                embed.title = f"war n°{war_id} removed"
                embed.description = "successfully deleted the war race data"

            else:
                embed.title = "action canceled"
                embed.description = "data remained unchanged"

        await interaction.edit_original_response(embed=embed, view=None)
