import discord

from discord import app_commands
from discord.ext import commands


class war_stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.id == 177162177432649728:
            return

        if len(message.embeds) >= 1:
            for embed in message.embeds:
                print(embed.to_dict())
        else:
            print(f"toad said: {message.content}")


async def setup(bot: commands.Bot):
    await bot.add_cog(war_stats(bot))
