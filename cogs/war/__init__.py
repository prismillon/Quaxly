from discord.ext import commands
from cogs.war.war_bot import WarBot
from cogs.war.war_stats import WarStats

class War(WarBot, WarStats):
    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(War(bot))