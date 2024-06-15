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
        if not discord.utils.find(
            lambda player: player["discordId"] == str(169497208406802432),
            lounge_data.data(),
        ):
            embed = discord.Embed(
                color=0x97F9D8,
                title="weird api response?",
                description=lounge_data.data(),
            )
            print(lounge_data.data())
            await self.bot.get_channel(1065611483897147502).send(
                text="<@169497208406802432> api error?", embed=embed
            )

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
