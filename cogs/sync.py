import discord

from typing import Literal, Optional
from discord.ext import commands
from discord.ext.commands import Greedy, Context


@commands.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
    ctx: Context,
    guilds: Greedy[discord.Object],
    spec: Optional[Literal["~", "*", "^"]] = None,
) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


@commands.command()
@commands.guild_only()
@commands.is_owner()
async def ext(ctx: Context) -> None:
    try:
        await ctx.bot.load_extension("cogs.extension")
    except Exception as error:
        await ctx.send(content=error)
    else:
        await ctx.send(content="succesfully loaded cogs.extension")


async def setup(bot: commands.Bot):
    bot.add_command(sync)
