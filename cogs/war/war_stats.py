import discord
from matplotlib.pylab import f
from numpy import average
import redis.asyncio as redis
import json

import redis as redis_sync

from discord import app_commands
from discord.ext import commands
from datetime import UTC, datetime
from utils import ConfirmButton, COLLATION
from cogs.war.base import Base
from autocomplete import track_autocomplete
from bson import ObjectId
from db import db

import utils

r = redis.Redis(host='redis', port=6379)
rs = redis_sync.Redis(host='redis', port=6379)


class WarStats(Base):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_toad_war = {}
        cached_war = rs.keys('*')

        for war in cached_war:
            war_data = rs.get(war)
            war_data = json.loads(war_data)
            war_data["_id"] = ObjectId(war_data["_id"])

            if "incoming_track" not in war_data:
                self.active_toad_war[int(war)] = war_data

    @commands.Cog.listener(name="on_message")
    async def toad_tracking(self, message: discord.Message):
        if message.author.id != 177162177432649728:
            return

        if "Started MK8DX 6v6" in message.content:
            extract_tag = message.content.replace("Started MK8DX 6v6: ", '')
            extract_tag = extract_tag[:-1].split(" vs ")
            tag = extract_tag[0]
            enemy_tag = extract_tag[1]
            date = datetime.now(UTC)

            self.active_toad_war[message.channel.id] = {
                "channel_id": message.channel.id,
                "date": date.isoformat(),
                "tag": tag,
                "enemy_tag": enemy_tag,
                "home_score": [],
                "enemy_score": [],
                "spots": [],
                "diff": [],
                "tracks": []
            }

            await db.Wars.insert_one(self.active_toad_war[message.channel.id])
            await r.set(message.channel.id, json.dumps(self.active_toad_war[message.channel.id], default=str))
            return

        if message.channel.id not in self.active_toad_war:
            return

        if "Stopped war." in message.content:
            if message.channel.id in self.active_toad_war:
                await r.delete(message.channel.id)
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
            self.active_toad_war[message.channel.id]['spots'].append(spots)
            self.active_toad_war[message.channel.id]['diff'].append(diff)
            self.active_toad_war[message.channel.id]['tracks'].append(track)
            self.active_toad_war[message.channel.id]['home_score'].append(41 + diff / 2)
            self.active_toad_war[message.channel.id]['enemy_score'].append(41 - diff / 2)

            await r.set(message.channel.id, json.dumps(self.active_toad_war[message.channel.id], default=str))
            war = self.active_toad_war[message.channel.id]
            await db.Wars.update_one({"_id": war["_id"]}, {
                "$set": {"spots": war['spots'], "diff": war['diff'], "tracks": war['tracks'],
                         "home_score": war['home_score'], "enemy_score": war['enemy_score']}})

        elif "Total Score after Race" in race_data['title']:
            race_id = int(race_data['title'].replace("Total Score after Race ", ''))
            self.active_toad_war[message.channel.id]['spots'] = self.active_toad_war[message.channel.id]['spots'][:race_id]
            self.active_toad_war[message.channel.id]['diff'] = self.active_toad_war[message.channel.id]['diff'][:race_id]
            self.active_toad_war[message.channel.id]['tracks'] = self.active_toad_war[message.channel.id]['tracks'][:race_id]
            self.active_toad_war[message.channel.id]['home_score'] = self.active_toad_war[message.channel.id]['home_score'][:race_id]
            self.active_toad_war[message.channel.id]['enemy_score'] = self.active_toad_war[message.channel.id]['enemy_score'][:race_id]
            await r.set(message.channel.id, json.dumps(self.active_toad_war[message.channel.id], default=str))
            war = self.active_toad_war[message.channel.id]
            await db.Wars.update_one({"_id": war["_id"]}, {
                "$set": {"spots": war['spots'], "diff": war['diff'], "tracks": war['tracks'],
                         "home_score": war['home_score'], "enemy_score": war['enemy_score']}})

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(channel="the channel you want to check stats from",
                           minimum="the minimum number of times the track has been played for it to count",
                           track="the track you want to check stats from")
    @app_commands.autocomplete(track=track_autocomplete)
    async def stats(self, interaction: discord.Interaction, channel: discord.TextChannel = None,
                    minimum: app_commands.Range[int, 1] = 1, track: str = None) -> None:
        """check race stats in the specified channel"""

        channel = channel or interaction.channel

        raw_stats = await db.Wars.find({"channel_id": channel.id}).to_list(None)

        track_stats = {}
        for war in raw_stats:
            for tracq, diff in zip(war['tracks'], war['diff']):
                if not tracq: continue
                if tracq not in track_stats:
                    track_stats[tracq] = []
                track_stats[tracq].append(diff)

        for tracq in track_stats:
            if len(track_stats[tracq]) < minimum:
                del track_stats[tracq]

        final_stats = {}
        for tracq in track_stats:
            final_stats[tracq] = {
                "average": round(average(track_stats[tracq])),
                "count": len(track_stats[tracq])
            }

        if track:
            if track not in final_stats:
                return await interaction.response.send_message(
                    content=f"no stats registered in this channel for the track {track}", ephemeral=True)
            embed = discord.Embed(color=0x47e0ff, title=f"stats for {track}")
            embed.add_field(name="average", value=final_stats[track]['average'], inline=True)
            embed.add_field(name="count", value=final_stats[track]['count'], inline=True)
            track_data = await db.Tracks.find_one({"trackName": track}, collation=COLLATION)
            embed.set_thumbnail(url=track_data['trackUrl'])
            return await interaction.response.send_message(embed=embed)

        if len(final_stats) == 0:
            return await interaction.response.send_message(content="no stats registered in this channel",
                                                           ephemeral=True)

        final_stats = {k: v for k, v in sorted(final_stats.items(), key=lambda item: item[1]['average'], reverse=True)}

        stats = [f"``{track:4} | {final_stats[track]['average']:>3} | {final_stats[track]['count']}``\n" for track in
                 final_stats]

        embeds = []

        for index, stat in enumerate(stats):
            if index % 10 == 0:
                embeds.append(discord.Embed(color=0x47e0ff, description="",
                                            title=f"race stats [ {index + 1} -> {index + 10 if len(stats) >= index + 10 else len(stats)} ]"))
            embeds[-1].description += stat

        await interaction.response.send_message(embed=embeds[0], view=utils.Paginator(interaction, embeds))

    @app_commands.command(name="list")
    @app_commands.guild_only()
    @app_commands.describe(channel="the channel you want to check wars from")
    async def warlist(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """check the list of war that have been recorded"""

        channel = channel or interaction.channel

        raw_stats = await db.Wars.find({"channel_id": channel.id}).to_list(None)

        if len(raw_stats) == 0:
            return await interaction.response.send_message(content="no wars registered in this channel", ephemeral=True)

        embeds = []

        for war in raw_stats:
            embed = discord.Embed(color=0x47e0ff, title=f"{war['tag']} vs {war['enemy_tag']}",
                                  timestamp=datetime.fromisoformat(war['date']))
            embed.add_field(name="final result", value=f"`{sum(war['diff']):+}`", inline=True)
            embed.add_field(name="war id", value=f"`{war['_id']}`", inline=True)
            embed.add_field(name="date", value=discord.utils.format_dt(datetime.fromisoformat(war['date'])), inline=True)
            race_text = "`\r"
            for index, track in enumerate(war['tracks']):
                if index == 20:
                    race_text += "[...]\n"
                    break
                race_text += f"{index+1:2}: {war['diff'][index]:>+3} | {track}\n"
            embed.add_field(name="race list", value=f"{race_text}`", inline=False)
            embeds.append(embed)

        if len(embeds) == 0:
            return await interaction.response.send_message(content="no wars to display in this channel", ephemeral=True)

        await interaction.response.send_message(embed=embeds[0], view=utils.Paginator(interaction, embeds))

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(channel="the channel you want to delete war from", war_id="the id of the war you want to delete")
    async def delete(self, interaction: discord.Interaction, channel: discord.TextChannel = None,
                     war_id: str = None):
        """delete stats from a specific war or all of them"""

        channel = channel or interaction.channel

        if not war_id:
            war_count = len(await db.Wars.find({"channel_id": channel.id}).to_list(None))
            if war_count == 0:
                return await interaction.response.send_message(content="this channel do not have any war stats",
                                                               ephemeral=True)

            embed = discord.Embed(color=0x47e0ff, title="delete all war stats")
            embed.description = f"you are about to delete {war_count} wars"
            view = ConfirmButton()
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            await view.wait()

            if view.answer:
                await db.Wars.delete_many({"channel_id": channel.id})
                embed.title = "war stats removed"
                embed.description = "all war stats have been removed"

            else:
                embed.title = "action canceled"
                embed.description = "data remained unchanged"

        else:
            war = await db.Wars.find({"_id": ObjectId(war_id), "channel_id": channel.id}).to_list(None)

            if len(war) != 1:
                return await interaction.response.send_message(
                    content="this war does not exist or does not belong to this channel", ephemeral=True)

            embed = discord.Embed(color=0x47e0ff, title=f"delete war n°{war_id}")
            embed.description = "you are about to delete this wars"
            view = ConfirmButton()

            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            await view.wait()

            if view.answer:
                await db.Wars.delete_one({"_id": ObjectId(war_id), "channel_id": channel.id})
                embed.title = f"war n°{war_id} removed"
                embed.description = "successfully deleted the war race data"

            else:
                embed.title = "action canceled"
                embed.description = "data remained unchanged"

        await interaction.edit_original_response(embed=embed, view=None)
