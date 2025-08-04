from discord.ext import commands

from cogs.dx.base import Base
from cogs.dx.delete_time import DeleteTimeCommands
from cogs.dx.display_time import DisplayTimeCommands
from cogs.dx.import_time import ImportTimeCommands
from cogs.dx.save_time import SaveTimeCommands


class Dx(
    Base, SaveTimeCommands, DeleteTimeCommands, DisplayTimeCommands, ImportTimeCommands
):
    """Mario Kart 8 Deluxe timetrial commands cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        ImportTimeCommands.__init__(self, bot)

    async def cog_unload(self):
        """Clean up when the cog is unloaded"""
        if hasattr(self, "_remove_user_task"):
            self._remove_user_task.cancel()


async def setup(bot: commands.Bot):
    await bot.add_cog(Dx(bot))
