import discord

from discord.ext import commands
from database import get_db_session
from models import User, UserServer


class DbSync(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_available(self, guild: discord.Guild):
        """Clean up database when guild becomes available - remove users who left"""
        await guild.chunk()

        member_ids = set()
        async for member in guild.fetch_members(limit=None):
            member_ids.add(member.id)

        with get_db_session() as session:
            users_in_server = (
                session.query(User, UserServer)
                .join(UserServer)
                .filter(UserServer.server_id == guild.id)
                .all()
            )

            for user, user_server in users_in_server:
                if user.discord_id not in member_ids:
                    session.delete(user_server)

            session.commit()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Remove user from server database when they leave"""
        with get_db_session() as session:
            user = session.query(User).filter(User.discord_id == member.id).first()

            if user:
                user_server = (
                    session.query(UserServer)
                    .filter(
                        UserServer.user_id == user.id,
                        UserServer.server_id == member.guild.id,
                    )
                    .first()
                )

                if user_server:
                    session.delete(user_server)
                    session.commit()


async def setup(bot: commands.Bot):
    await bot.add_cog(DbSync(bot))
