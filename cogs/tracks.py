import discord
import sql

from discord import app_commands

class cupsButtons(discord.ui.View):
    def __init__(self, embed: discord.Embed, ctx: discord.Interaction, clicked_cup: str = None):
        super().__init__()
        self.embed = embed
        self.ctx = ctx
        self.clicked_cup = clicked_cup
        for cup in sql.get_cups_emoji():
            button = discord.ui.Button(emoji=f"<:{cup[0]}:{cup[1]}>")
            if cup[0] == clicked_cup:
                button.disabled = True
            button.callback = lambda i, cup_identifier=cup[0]: self.callback(i, cup_identifier)
            self.add_item(button)

    async def callback(self, ctx: discord.Interaction, cup: str):
        self.stop()
        tracks = sql.get_tracks_from_cup(cup)
        self.embed.title = tracks[0][1]
        self.embed.set_thumbnail(url=tracks[0][2])
        self.embed.description = f"```{tracks[0][0]},   {tracks[1][0]},   {tracks[2][0]},   {tracks[3][0]}```"
        view = cupsButtons(self.embed, self.ctx, cup)
        return await ctx.response.edit_message(embed=self.embed, view=view)
    
    async def on_timeout(self):
        return await self.ctx.edit_original_response(view=None)


@app_commands.command()
@app_commands.guild_only()
async def tracks(ctx: discord.Interaction):
    """List of all the tracks in the game"""

    embed = discord.Embed(color=0x47e0ff, description="Here is the list of all the cups in Mario Kart 8 Deluxe", title="Tracks")
    embed.set_thumbnail(url=ctx.guild.icon)
    view = cupsButtons(embed=embed, ctx=ctx)
    return await ctx.response.send_message(embed=embed, view=view)