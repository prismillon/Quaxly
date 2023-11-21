import discord
import re

import utils
import sql

from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from datetime import datetime, timedelta


class import_time(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_user = {}
        self._remove_user_task = self.remove_expired_user.start()

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(speed="the mode your list correspond to", items="is it with shroom or not")
    @app_commands.choices(speed=utils.speedChoices, items=utils.itemChoices)
    async def import_time(self, interaction: discord.Interaction, speed: Choice[str], items: Choice[str]):
        """import time from cadoizzob"""

        self.active_user[interaction.user.global_name] = {"date": datetime.now(), "mode": items.value+speed.value, "discord_id": interaction.user.id}
        await interaction.response.send_message("please use the command below quaxly will register the times from Cadoizzob for you")
        await interaction.channel.send(f"/tt option:{speed.name} categorie:{'shroom' if items.value == 'Sh' else 'ni'} third:find four:{interaction.user.id}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id != 543424033673445378 or len(message.embeds) != 1 or message.embeds[0].title[9:] not in self.active_user.keys():
            return

        correct_track_names = sql.get_all_tracks()
        user = self.active_user.get(message.embeds[0].title[9:])
        time_list = re.findall("[a-zA-Z0-9]+ : \*\*\d+\/\d+\*\* -> \d:[0-5]\d\.\d{3}", message.embeds[0].description)
        if len(time_list) == 0:
            return await message.channel.send("ptit flop bg")
        for line in time_list:
            time = line.split(" -> ")[1]
            track = line.split(" : ")[0]
            if track.lower() == "bcm64":
                track = "bCMo"
            elif track.lower() == "bcmw":
                track = "bCMa"
            else:
                track = next(track_name[0] for track_name in correct_track_names if track_name[0].lower() == track.lower())
            try:
                sql.save_time(user["mode"], user["discord_id"], track, time)
            except:
                pass

        await message.add_reaction("✅")
        await message.channel.send("Successfully processed your times !")
        self.active_user.pop(message.embeds[0].title[9:])


    @tasks.loop(minutes=1)
    async def remove_expired_user(self):
        expired_date = datetime.now()-timedelta(minutes=10)
        for user, data in list(self.active_user.items()):
            if data['date'] < expired_date:
                self.active_user.pop(user)


async def setup(bot: commands.Bot):
    await bot.add_cog(import_time(bot))