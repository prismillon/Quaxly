import discord

from utils import lounge_data, mkc_data, lounge_season
from discord.ext import commands, tasks


class Startup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._api_list_task = self.api_list.start()

    @tasks.loop(minutes=10)
    async def api_list(self):
        await lounge_data.lounge_api_full()
        await mkc_data.mkc_api_full()
        await lounge_season.lounge_season()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.bot.guilds)} servers",
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Startup(bot))
