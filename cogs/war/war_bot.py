import discord
import json
import re

from datetime import datetime, timedelta, UTC
from discord.ext import commands, tasks
from discord import app_commands
from cogs.war.base import Base
from bson import ObjectId
from autocomplete import mkc_tag_autocomplete
from db import db, rs, r
from utils import COLLATION


_SCORE = (15, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)


def text_to_score(text: str):
    data = []
    prev = None
    next_list = []
    loopFlag = False
    while text:
        next_list = []
        if text.startswith("-"):
            loopFlag = True
            text = text[1:]
            if data:
                prev = data[-1]
            else:
                prev = 0
        if text.startswith("0"):
            next_list = [10]
            text = text[1:]
        elif text.startswith("+"):
            next_list = [11]
            text = text[1:]
        elif text.startswith("10"):
            next_list = [10]
            text = text[2:]
        elif text.startswith("110"):
            next_list = [1, 10]
            text = text[3:]
        elif text.startswith("1112"):
            next_list = [11, 12]
            text = text[4:]
        elif text.startswith("111"):
            next_list = [1, 11]
            text = text[3:]
        elif text.startswith("112"):
            next_list = [1, 12]
            text = text[3:]
        elif text.startswith("11"):
            next_list = [11]
            text = text[2:]
        elif text.startswith("12"):
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
                data.append(prev + 1)
                prev += 1
            loopFlag = False
        data += next_list
    return validate_score(set(data))


def validate_score(data: int):
    last_spot = 12
    while len(data) < 6:
        data.add(last_spot)
        last_spot -= 1
    return sorted(list(data))[:6]


def make_embed(war):
    embed = discord.Embed(
        color=0x47E0FF, title=f"Total Score after Race {len(war['diff'])}"
    )
    diff = sum(war["home_score"]) - sum(war["enemy_score"])
    embed.add_field(name=war["tag"], value=sum(war["home_score"]))
    embed.add_field(name=war["enemy_tag"], value=sum(war["enemy_score"]))
    embed.add_field(
        name="Difference",
        value=f"{diff if diff < 0 else '+' + str(diff)}",
        inline=False,
    )
    if len(war["diff"]) > 0:
        race_field_value = "```\n"
        for i, (spot, diff, track) in enumerate(
            zip(war["spots"], war["diff"], war["tracks"])
        ):
            diff = str(diff) if diff < 0 else "+" + str(diff)
            spot = re.sub("[\\[\\] ]", "", str(spot))
            race_field_value += f"{i + 1:2}: {diff:>3} | {spot:14} {'(' + track + ')' if track else ''}\n"
        race_field_value += "```"
        embed.add_field(name="Races", value=race_field_value, inline=False)
    return embed


class WarBot(Base):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_war = {}
        cached_war = rs.keys("*")

        for war in cached_war:
            war_data = rs.get(war)
            war_data = json.loads(war_data)
            war_data["_id"] = ObjectId(war_data["_id"])

            if "incoming_track" in war_data:
                self.active_war[int(war)] = war_data

        self._remove_war_task = self.remove_expired_war.start()

    @app_commands.command(name="start")
    @app_commands.guild_only()
    @app_commands.autocomplete(tag=mkc_tag_autocomplete, enemy_tag=mkc_tag_autocomplete)
    @app_commands.describe(
        tag="the tag of your team", enemy_tag="the tag of the enemy team"
    )
    async def warstart(
        self, interaction: discord.Interaction, tag: str, enemy_tag: str
    ):
        """start a war in the channel"""

        date = datetime.now(UTC)
        self.active_war[interaction.channel.id] = {
            "channel_id": interaction.channel.id,
            "date": date.isoformat(),
            "tag": tag,
            "enemy_tag": enemy_tag,
            "home_score": [],
            "enemy_score": [],
            "spots": [],
            "diff": [],
            "tracks": [],
            "incoming_track": None,
        }
        await db.Wars.insert_one(self.active_war[interaction.channel.id])
        await r.set(
            interaction.channel.id,
            json.dumps(self.active_war[interaction.channel.id], default=str),
        )
        return await interaction.response.send_message(
            f"started war between `{tag}` and `{enemy_tag}` \n(obs overlay: https://waroverlay.prismillon.com/overlay/{interaction.channel.id})"
        )

    @app_commands.command(name="stop")
    @app_commands.guild_only()
    async def warstop(self, interaction: discord.Interaction):
        """stop the war"""

        if interaction.channel.id in self.active_war:
            await r.delete(interaction.channel.id)
            self.active_war.pop(interaction.channel.id)
            return await interaction.response.send_message("stopped war")
        await interaction.response.send_message("no active war")

    @tasks.loop(minutes=1)
    async def remove_expired_war(self):
        expired_date = datetime.now(UTC) - timedelta(hours=3)
        for channel_id, data in list(self.active_war.items()):
            if datetime.fromisoformat(data["date"]) < expired_date:
                await r.delete(channel_id)
                self.active_war.pop(channel_id)

    @commands.Cog.listener(name="on_message")
    async def war_score(self, message: discord.Message):
        if message.channel.id not in self.active_war or message.content == "":
            return

        war = self.active_war[message.channel.id]

        if message.content.startswith("race "):
            data = message.content.split(" ")
            if not data[1].isnumeric() or len(data) != 3:
                return
            track = await db.Tracks.find_one(
                {"trackName": data[2]}, collation=COLLATION
            )
            print(track)
            if not track:
                return
            war["tracks"][int(data[1]) - 1] = track["trackName"]
            self.active_war[message.channel.id] = war
            await db.Wars.update_one(
                {"_id": war["_id"]}, {"$set": {"tracks": war["tracks"]}}
            )
            await r.set(
                message.channel.id,
                json.dumps(self.active_war[message.channel.id], default=str),
            )
            return await message.reply(embed=make_embed(war), mention_author=False)

        if " " in message.content:
            return

        if message.content.lower() == "back":
            race_id = len(war["spots"])
            war["spots"] = war["spots"][: race_id - 1]
            war["diff"] = war["diff"][: race_id - 1]
            war["tracks"] = war["tracks"][: race_id - 1]
            war["home_score"] = war["home_score"][: race_id - 1]
            war["enemy_score"] = war["enemy_score"][: race_id - 1]
            await db.Wars.update_one(
                {"_id": war["_id"]},
                {
                    "$set": {
                        "spots": war["spots"],
                        "diff": war["diff"],
                        "tracks": war["tracks"],
                        "home_score": war["home_score"],
                        "enemy_score": war["enemy_score"],
                    }
                },
            )
            self.active_war[message.channel.id] = war
            await r.set(
                message.channel.id,
                json.dumps(self.active_war[message.channel.id], default=str),
            )
            return await message.reply(embed=make_embed(war), mention_author=False)

        if re.fullmatch("^((?!--)[0-9+-])+$", message.content):
            spots = text_to_score(message.content)
            scored = sum(map(lambda r: _SCORE[r - 1], spots))
            war["spots"].append(spots)
            war["home_score"].append(scored)
            war["enemy_score"].append(82 - scored)
            war["diff"].append(war["home_score"][-1] - war["enemy_score"][-1])
            war["tracks"].append(war["incoming_track"])
            war["incoming_track"] = None
            await db.Wars.update_one(
                {"_id": war["_id"]},
                {
                    "$set": {
                        "spots": war["spots"],
                        "diff": war["diff"],
                        "tracks": war["tracks"],
                        "home_score": war["home_score"],
                        "enemy_score": war["enemy_score"],
                    }
                },
            )
            self.active_war[message.channel.id] = war
            await r.set(
                message.channel.id,
                json.dumps(self.active_war[message.channel.id], default=str),
            )
            return await message.reply(embed=make_embed(war), mention_author=False)

        track = await db.Tracks.find_one(
            {"trackName": message.content}, collation=COLLATION
        )

        if track:
            war["incoming_track"] = track["trackName"]
            return await message.reply(
                embed=discord.Embed(
                    color=0x47E0FF, title=f"{track['trackName']} | {track['fullName']}"
                ).set_image(
                    url=f"http://japan-mk.blog.jp/mk8dx.info-4/table/{track['id']:02d}.jpg"
                ),
                mention_author=False,
            )
