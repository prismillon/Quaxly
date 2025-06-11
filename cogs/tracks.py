import discord
from typing import List, Optional

from discord import app_commands
from discord.app_commands import Choice
from database import get_db_session
from discord.ext import commands
from models import Cup, Track, GAME_MK8DX, GAME_MKWORLD
from game_utils import get_game_tracks, get_game_cups


class CupsButtons(discord.ui.View):
    def __init__(
        self,
        embed: discord.Embed,
        interaction: discord.Interaction,
        cups: List[Cup],
        tracks: List[Track],
        clicked_cup: Optional[str] = None,
    ):
        super().__init__(timeout=300)
        self.embed: discord.Embed = embed
        self.interaction: discord.Interaction = interaction
        self.cups: List[Cup] = cups
        self.tracks: List[Track] = tracks
        self.clicked_cup: Optional[str] = clicked_cup

        for cup in self.cups:
            if cup.cup_emoji_name and cup.cup_emoji_id:
                button: discord.ui.Button = discord.ui.Button(
                    emoji=f"<:{cup.cup_emoji_name}:{cup.cup_emoji_id}>"
                )
            else:
                button: discord.ui.Button = discord.ui.Button(label=cup.cup_name[:20])

            if cup.cup_emoji_name == clicked_cup:
                button.disabled = True
            button.callback = (
                lambda i, cup_identifier=cup.cup_emoji_name: self.callback(
                    i, cup_identifier
                )
            )
            self.add_item(button)

    async def callback(
        self, interaction: discord.Interaction, cup_identifier: str
    ) -> None:
        self.stop()
        selected_cup: Optional[Cup] = next(
            (cup for cup in self.cups if cup.cup_emoji_name == cup_identifier), None
        )
        if not selected_cup:
            return

        self.embed.clear_fields()
        self.embed.title = selected_cup.cup_name
        if selected_cup.cup_url:
            self.embed.set_thumbnail(url=selected_cup.cup_url)

        cup_tracks: List[Track] = [
            track for track in self.tracks if track.cup_id == selected_cup.id
        ]
        cup_tracks.sort(key=lambda x: x.track_id)

        self.embed.description = ""
        for track in cup_tracks:
            self.embed.add_field(
                name=track.full_name, value=track.track_name, inline=False
            )

        view: CupsButtons = CupsButtons(
            self.embed,
            self.interaction,
            self.cups,
            self.tracks,
            selected_cup.cup_emoji_name,
        )
        return await interaction.response.edit_message(embed=self.embed, view=view)

    async def on_timeout(self) -> None:
        try:
            await self.interaction.edit_original_response(view=None)
        except:
            pass


@app_commands.command()
@app_commands.guild_only()
@app_commands.describe(game="which game do you want to see tracks for?")
@app_commands.choices(
    game=[
        Choice(name="Mario Kart 8 Deluxe", value=GAME_MK8DX),
        Choice(name="Mario Kart World", value=GAME_MKWORLD),
    ]
)
async def tracks(
    interaction: discord.Interaction, game: Optional[Choice[str]] = None
) -> None:
    """List of all the tracks in the specified game"""

    selected_game: str = game.value if game else GAME_MK8DX
    game_name: str = (
        "Mario Kart 8 Deluxe" if selected_game == GAME_MK8DX else "Mario Kart World"
    )

    embed: discord.Embed = discord.Embed(
        color=0x47E0FF,
        title=f"{game_name} Tracks",
    )
    if interaction.guild and interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon)

    with get_db_session() as session:
        if selected_game == GAME_MKWORLD:
            tracks_list: List[Track] = get_game_tracks(session, selected_game)

            if not tracks_list:
                return await interaction.response.send_message(
                    f"No tracks found for {game_name}. Make sure the database is properly set up.",
                    ephemeral=True,
                )

            description: str = f"**{game_name} Track List**\n\n"

            for track in tracks_list:
                description += f"**{track.full_name}** - `{track.track_name}`\n"

            embed.description = description

            return await interaction.response.send_message(embed=embed)

        else:
            cups: List[Cup] = get_game_cups(session, selected_game)

            if not cups:
                return await interaction.response.send_message(
                    f"No cups found for {game_name}. Make sure the database is properly set up.",
                    ephemeral=True,
                )

            tracks_list: List[Track] = get_game_tracks(session, selected_game)

            for cup in cups:
                _ = cup.id
                _ = cup.cup_name
                _ = cup.cup_emoji_name
                _ = cup.cup_emoji_id
                _ = cup.cup_url

            for track in tracks_list:
                _ = track.id
                _ = track.cup_id
                _ = track.track_id
                _ = track.full_name
                _ = track.track_name

            session.expunge_all()

            embed.description = f"Here is the list of all the cups in {game_name}"

            view: CupsButtons = CupsButtons(
                embed=embed,
                interaction=interaction,
                cups=cups,
                tracks=tracks_list,
            )

            return await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    bot.tree.add_command(tracks)
