import aiohttp
import discord

from discord.app_commands import Choice

allowed_tables = ['Sh150', 'Ni150', 'Sh200', 'Ni200']
speedChoices = [Choice(name='150cc', value='150'), Choice(name='200cc', value='200')]
itemChoices = [Choice(name='Shrooms', value='Sh'), Choice(name='No items', value='Ni')]
statChoices = [Choice(name='mmr', value='mmr'), Choice(name='peak', value='maxMmr'), Choice(name='events', value='eventsPlayed')]


async def wait_for_chunk(ctx: discord.Interaction):
    await ctx.response.send_message(content="server is not loaded yet, please wait, this message will be edited when this server is ready")
    message = ctx.original_response()
    await ctx.guild.chunk()
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

    @property
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

    @property
    def data(self):
        return self._data


mkc_data = mkcData()
lounge_data = loungeData()
