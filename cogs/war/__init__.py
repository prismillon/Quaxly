from cogs.war.war_bot import war_bot
from cogs.war.war_stats import war_stats
from discord.ext import commands

class war(war_bot, war_stats):
    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(war(bot))