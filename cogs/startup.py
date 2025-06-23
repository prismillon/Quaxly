import discord

from utils import lounge_data, mkc_data, lounge_season
from discord.ext import commands, tasks


class Startup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._api_list_task = self.api_list.start()

    @tasks.loop(minutes=10)
    async def api_list(self):
        await lounge_season.lounge_season()
        test_player = await lounge_data.find_player_by_discord_id(
            169497208406802432, "mkworld"
        )
        if not test_player:
            embed = discord.Embed(
                color=0x97F9D8,
                title="weird api response?",
                description="Could not find test player - API may be down",
            )
            print("Lounge API test failed - could not find test player")
            await self.bot.get_channel(1065611483897147502).send(
                content="<@169497208406802432> api error?", embed=embed
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
