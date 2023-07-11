import discord
import aiohttp
import datetime
import re

from typing import List
from discord import app_commands


async def get_host_string(host: str, ctx: discord.Interaction):
    url = "https://www.mk8dx-lounge.com/api/player?"

    if re.match("^([0-9]{4}-){2}[0-9]{4}$", host):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}fc={host}") as response:
                json_data = await response.json()
        return f"{host} (<@{json_data['discordId']}>)"

    elif ctx.guild.get_member(int(re.findall("[0-9]+", host)[0])) != None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}discordid={re.findall('[0-9]+', host)[0]}") as response:
                json_data = await response.json()
        return f"{json_data['switchFc']} (<@{json_data['discordId']}>)" if response.status == 200 else host

    else:
        return host


class editLineup(discord.ui.View):
    def __init__(self, old_view: discord.ui.View):
        super().__init__(timeout=60)
        self.old_view = old_view

    @discord.ui.select(cls=discord.ui.UserSelect, min_values=1, max_values=6)
    async def edit_lineup(self, ctx: discord.Interaction, users: List[discord.Member]):
        self.old_view.embed.remove_field(0)
        self.old_view.embed.insert_field_at(0, name="lineup", value=' - '.join(user.mention for user in sorted(users.values, key=lambda user: user.display_name.lower())), inline=False)
        await ctx.response.edit_message(embed=self.old_view.embed, view=self.old_view)
        self.stop()
    
    async def on_timeout(self):
        await self.old_view.ctx.edit_original_response(view=self.old_view)


class editModal(discord.ui.Modal, title='edit lineup'):
    def __init__(self, embed: discord.Embed):
        super().__init__()
        self.embed = embed

    time = discord.ui.TextInput(label='time', required=False)
    host = discord.ui.TextInput(label='host', required=False)
    ennemy_tag = discord.ui.TextInput(label='ennemy tag', required=False)
    tag = discord.ui.TextInput(label='tag', required=False)

    async def on_submit(self, ctx: discord.Interaction):
        await ctx.response.defer()

        if self.time.value != '':
            self.embed.remove_field(1)
            self.embed.insert_field_at(1, name="open", value=f"`{self.time.value}`", inline=True)

        if self.host.value != '':
            self.embed.remove_field(2)
            self.embed.insert_field_at(2, name="host", value=await get_host_string(self.host.value, ctx), inline=True)

        if self.ennemy_tag.value != '' and self.tag.value != '':
            self.embed.title = f"clan war | {self.tag.value} vs {self.ennemy_tag.value}"
        elif self.ennemy_tag.value != '':
            self.embed.title = re.sub(r"(\|.*?vs\s+)(\S+)$", r"\1" + self.ennemy_tag.value, self.embed.title)
        elif self.tag.value != '':
            self.embed.title = re.sub(r"(\| )(\S+)( vs \S+)$", r"\1" + self.tag.value + r"\3", self.embed.title)

        await ctx.edit_original_response(embed=self.embed)


class editButtons(discord.ui.View):
    def __init__(self, embed: discord.Embed, ctx: discord.Interaction):
        super().__init__(timeout=21600)
        self.ctx = ctx
        self.embed = embed

    @discord.ui.button(emoji='📝', style=discord.ButtonStyle.gray)
    async def edit(self, ctx: discord.Interaction, button: discord.ui.Button):
        modal = editModal(self.embed)
        await ctx.response.send_modal(modal)

    @discord.ui.button(emoji='👥', style=discord.ButtonStyle.gray)
    async def players(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.edit_message(view=editLineup(self))

    async def on_timeout(self):
        await self.ctx.edit_original_response(view=None)


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(players="List of the players for this lineup (you have to tag them)", time="The time of the war is schedueled for. Any format", host="Friend code or tag the host of the war", ennemy_tag="Name or tag of the ennemy team", tag="Name or tag of your team")
async def lineup(ctx: discord.Interaction, players: str, time: str, host: str, ennemy_tag: str, tag: str):
    """create a clan war line-up for your team"""

    embed = discord.Embed(color=0x47e0ff, title=f"clan war | {tag} vs {ennemy_tag}").set_thumbnail(url=ctx.guild.icon)
    member_string = ' - '.join(player.mention for player in sorted([ctx.guild.get_member(int(player)) for player in re.findall("[0-9]+", players) if ctx.guild.get_member(int(player))], key=lambda user: user.display_name.lower()))
    host_string = await get_host_string(host, ctx)

    embed.add_field(name="lineup", value=member_string, inline=False)
    embed.add_field(name="open", value=f"`{time}`", inline=True)
    embed.add_field(name="host", value=host_string, inline=True)

    await ctx.response.send_message(content=f"lineup war {time} vs {ennemy_tag} || {member_string} ||", embed=embed, view=editButtons(embed, ctx))
    await ctx.edit_original_response(content=None)