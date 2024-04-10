import discord

from discord.ext import commands
from db import db


class DbSync(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_available(self, guild: discord.Guild):
        await guild.chunk()
        members_id = [member.id async for member in guild.fetch_members(limit=None)]
        users_from_server = await db.Users.find({"servers.serverId": guild.id}).to_list(
            None
        )
        for member in users_from_server:
            if member["discordId"] not in members_id:
                await db.Users.update_one(
                    {"discordId": member["discordId"]},
                    {"$pull": {"servers": {"serverId": guild.id}}},
                )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await db.Users.update_one(
            {"discordId": member.id},
            {"$pull": {"servers": {"serverId": member.guild.id}}},
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(DbSync(bot))
