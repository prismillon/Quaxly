import discord

from discord.ext import commands

import sql

class DbSync(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_available(self, guild: discord.Guild):
        await guild.chunk()
        members_id = [member.id async for member in guild.fetch_members(limit=None)]
        for member in sql.get_all_users_from_server(guild.id):
            if member[0] not in members_id:
                sql.delete_player_from_server(member[0], guild.id)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        sql.delete_player_from_server(member.id, member.guild.id)


async def setup(bot: commands.Bot):
    await bot.add_cog(DbSync(bot))