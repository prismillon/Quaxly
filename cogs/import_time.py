import re
import discord

from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from db import db

import utils


class ImportTime(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_user = {}
        self._remove_user_task = self.remove_expired_user.start()

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(
        speed="the mode your list correspond to",
        items="is it with shroom or not",
        name="the name cadoizzob display",
    )
    @app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
    async def import_time(
        self,
        interaction: discord.Interaction,
        speed: Choice[str],
        items: Choice[str],
        name: str = None,
    ):
        """import time from cadoizzob"""

        if not interaction.channel.permissions_for(interaction.guild.me).send_messages:
            return await interaction.response.send_message(
                "I don't have permission to send message in this channel"
            )

        name = name or interaction.user.display_name

        self.active_user[name.lower()] = {
            "date": datetime.now(),
            "mode": items.value + speed.value + "Tracks",
            "discord_id": interaction.user.id,
        }
        await interaction.response.send_message(
            "please use the command below quaxly will register the times from Cadoizzob for you (make sure your name match the name in cadoizzob)"
        )
        await interaction.channel.send(
            f"/tt option:{speed.name} categorie:{'shroom' if items.value == 'Sh' else 'ni'} third:find four:{interaction.user.id}"
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (
            message.author.id != 543424033673445378
            or len(message.embeds) != 1
            or message.embeds[0].title[9:].lower() not in self.active_user.keys()
        ):
            return

        correct_track_names = await db.Tracks.find({}, {"trackName": 1}).to_list(None)
        mode = self.active_user[message.embeds[0].title[9:].lower()]["mode"]
        user = await db.Users.find_one(
            {
                "discordId": self.active_user[message.embeds[0].title[9:].lower()][
                    "discord_id"
                ]
            }
        )
        if not user:
            user = {
                "discordId": self.active_user[message.embeds[0].title[9:].lower()][
                    "discord_id"
                ],
                "servers": [],
                mode: [],
            }
        time_list = re.findall(
            "[a-zA-Z0-9]+ : \*\*\d+\/\d+\*\* -> \d:[0-5]\d\.\d{3}",
            message.embeds[0].description,
        )
        if len(time_list) == 0:
            return await message.channel.send("ptit flop bg")
        for line in time_list:
            time = line.split(" -> ")[1]
            track = line.split(" : ")[0]
            if track.lower() == "bcm64":
                track = "bCMo"
            elif track.lower() == "bcmw":
                track = "bCMa"
            elif track.lower() == "brrd":
                track = "bRRW"
            elif track.lower() == "bsis":
                track = "bSSy"
            else:
                track = discord.utils.find(
                    lambda x: x["trackName"].lower() == track.lower(),
                    correct_track_names,
                )
            if track in user[mode]:
                user[mode][user[mode].index(track)]["time"] = time
            else:
                user[mode].append({"trackRef": track["_id"], "time": time})

        await db.Users.update_one(
            {"discordId": user["discordId"]}, {"$set": {mode: user[mode]}}
        )
        await message.add_reaction("✅")
        await message.channel.send("Successfully processed your times !")
        self.active_user.pop(message.embeds[0].title[9:].lower())

    @tasks.loop(minutes=1)
    async def remove_expired_user(self):
        expired_date = datetime.now() - timedelta(minutes=10)
        for user, data in list(self.active_user.items()):
            if data["date"] < expired_date:
                self.active_user.pop(user)


async def setup(bot: commands.Bot):
    await bot.add_cog(ImportTime(bot))
