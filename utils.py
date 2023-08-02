import aiohttp
import discord
import asyncio

from typing import List
from discord.app_commands import Choice

allowed_tables = ['Sh150', 'Ni150', 'Sh200', 'Ni200']
speedChoices = [Choice(name='150cc', value='150'), Choice(name='200cc', value='200')]
itemChoices = [Choice(name='Shrooms', value='Sh'), Choice(name='No items', value='Ni')]
statChoices = [Choice(name='mmr', value='mmr'), Choice(name='peak', value='maxMmr'), Choice(name='events', value='eventsPlayed')]


async def wait_for_chunk(interaction: discord.Interaction):
    await interaction.response.send_message(content="server is not loaded yet, please wait, this message will be edited when this server is ready")
    message = await interaction.original_response()
    await interaction.guild.chunk()
    await message.edit(content="server is now ready! ✅")


class loungeData:
    def __init__(self):
        self._data = None

    async def lounge_api_full(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.mk8dx-lounge.com/api/player/list") as response:
                if response.status == 200:
                    _data_full = await response.json()
                    self._data = [player for player in _data_full['players'] if "discordId" in player]

    def data(self):
        return self._data


class mkcData:
    def __init__(self):
        self._data = None

    async def mkc_api_full(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.mariokartcentral.com/mkc/api/registry/teams/category/150cc") as response:
                if response.status == 200:
                    _data_full = await response.json()
                    self._data = _data_full['data']

    def data(self):
        return self._data


class Paginator(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, embeds: List[discord.Embed]):
        super().__init__(timeout=600)
        self.interaction = interaction
        self.embeds = embeds
        self.page_num = 1
        self.index.label = f"1/{len(embeds)}"
        self.first.disabled = True
        self.before.disabled = True
        if len(embeds) == 1:
            self.after.disabled = True
            self.last.disabled = True

    @discord.ui.button(label='<<', style=discord.ButtonStyle.blurple)
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_num = 1
        self.index.label = f"{self.page_num}/{len(self.embeds)}"
        self.first.disabled = True
        self.before.disabled = True
        self.after.disabled = False
        self.last.disabled = False
        await interaction.response.edit_message(embed=self.embeds[self.page_num-1], view=self)

    @discord.ui.button(label='<', style=discord.ButtonStyle.red)
    async def before(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_num -= 1
        self.index.label = f"{self.page_num}/{len(self.embeds)}"
        self.after.disabled = False
        self.last.disabled = False
        if self.page_num == 1:
            self.first.disabled = True
            self.before.disabled = True
        await interaction.response.edit_message(embed=self.embeds[self.page_num-1], view=self)

    @discord.ui.button(style=discord.ButtonStyle.gray, disabled=True)
    async def index(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label='>', style=discord.ButtonStyle.green)
    async def after(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_num += 1
        self.index.label = f"{self.page_num}/{len(self.embeds)}"
        self.first.disabled = False
        self.before.disabled = False
        if self.page_num == len(self.embeds):
            self.after.disabled = True
            self.last.disabled = True
        await interaction.response.edit_message(embed=self.embeds[self.page_num-1], view=self)

    @discord.ui.button(label='>>', style=discord.ButtonStyle.blurple)
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page_num = len(self.embeds)
        self.index.label = f"{self.page_num}/{len(self.embeds)}"
        self.first.disabled = False
        self.before.disabled = False
        self.after.disabled = True
        self.last.disabled = True
        await interaction.response.edit_message(embed=self.embeds[self.page_num-1], view=self)

    async def on_timeout(self):
        self.first.disabled = True
        self.before.disabled = True
        self.after.disabled = True
        self.last.disabled = True
        await self.interaction.edit_original_response(view=self)


class confirmButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.answer = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.answer = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.answer = False
        self.stop()


mkc_data = mkcData()
lounge_data = loungeData()