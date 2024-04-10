import discord

from discord import app_commands
from db import db


class CupsButtons(discord.ui.View):
    def __init__(
        self,
        embed: discord.Embed,
        interaction: discord.Interaction,
        cups,
        tracks,
        clicked_cup: str = None,
    ):
        super().__init__()
        self.embed = embed
        self.interaction = interaction
        self.cups = cups
        self.tracks = tracks
        self.clicked_cup = clicked_cup
        for cup in self.cups:
            button = discord.ui.Button(
                emoji=f"<:{cup['cupEmojiName']}:{cup['cupEmojiId']}>"
            )
            if cup["cupEmojiName"] == clicked_cup:
                button.disabled = True
            button.callback = lambda i, cup_identifier=cup[
                "cupEmojiName"
            ]: self.callback(i, cup_identifier)
            self.add_item(button)

    async def callback(self, interaction: discord.Interaction, cup: str):
        self.stop()
        cup = discord.utils.find(lambda x: x["cupEmojiName"] == cup, self.cups)
        self.embed.clear_fields()
        self.embed.title = cup["cupName"]
        self.embed.set_thumbnail(url=cup["cupUrl"])
        tracks = [track for track in self.tracks if track["cupId"] == cup["_id"]]
        self.embed.description = ""
        for track in tracks:
            self.embed.add_field(
                name=track["fullName"], value=track["trackName"], inline=False
            )
        view = CupsButtons(
            self.embed, self.interaction, self.cups, self.tracks, cup["cupEmojiName"]
        )
        return await interaction.response.edit_message(embed=self.embed, view=view)

    async def on_timeout(self):
        return await self.interaction.edit_original_response(view=None)


@app_commands.command()
@app_commands.guild_only()
async def tracks(interaction: discord.Interaction):
    """List of all the tracks in the game"""

    embed = discord.Embed(
        color=0x47E0FF,
        description="Here is the list of all the cups in Mario Kart 8 Deluxe",
        title="Tracks",
    )
    embed.set_thumbnail(url=interaction.guild.icon)
    cups = await db.Cups.find({}).to_list(None)
    cups = sorted(cups, key=lambda x: x["id"])
    tracks = await db.Tracks.find({}).to_list(None)
    tracks = sorted(tracks, key=lambda x: x["id"])
    view = CupsButtons(embed=embed, interaction=interaction, cups=cups, tracks=tracks)
    return await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    bot.tree.add_command(tracks)
