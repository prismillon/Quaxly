from discord.ext import commands

from cogs.war.war_bot import WarBot
from cogs.war.war_stats import WarStats


class War(WarBot, WarStats):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        WarBot.__init__(self, bot)
        WarStats.__init__(self, bot)


async def setup(bot: commands.Bot):
    await bot.add_cog(War(bot))
