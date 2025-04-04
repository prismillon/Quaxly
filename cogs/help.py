import discord

from discord import app_commands
from discord.ext import commands
from utils import Paginator


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def help(self, interaction: discord.Interaction):
        """show Quaxly help menu"""

        embeds = [discord.Embed(color=0x47E0FF, title="Time Trials commands")]

        embeds[-1].add_field(
            name="register user",
            value="```/register```this command is useful when you just joined your server but you are already using the bot in other servers, it will add you in the server list",
        )
        embeds[-1].add_field(
            name="remove user",
            value="```/remove_user (player)```this command is useful when someone want to be removed from the list but want to stay in the server, it will remove the user from the list (you if not provided), this command is not needed when someone leave the server, in this case the user is automatically removed",
        )
        embeds[-1].add_field(
            name="save time",
            value="```/save_time speed items track time```this command save a time, if your time is better than the previous one it will override it, if not a confirmation prompt will be showed if you still want to override (you will be registered in the server if you were not already)",
            inline=False,
        )
        embeds[-1].add_field(
            name="delete time",
            value="```/delete_time (speed) (items) (track) (time)```this command delete times, all conditions are optional, the bot will delete times that respect the conditions provided, this command always show a confirmation prompt with all the times that are going to be removed",
        )
        embeds[-1].add_field(
            name="display time",
            value="```/display_time speed items (track) (player)```this command show times from users that are registered in the server, track and player are optionnal, if you do not provide any it will show the best time on each track and who own it, if track is selected it will show the ranking on the track, if player is selected it will show the user times or the users in the role",
            inline=False,
        )

        embeds.append(discord.Embed(color=0x47E0FF, title="Lounge commands"))

        embeds[-1].add_field(
            name="role stats",
            value="```/role_stats role (stat) (season)```show the stats of everyone in a role, the total average and the 6 best average, stat let you choose the type of stats (default is mmr), season let you choose the season to check the stats from (default to current season)",
            inline=False,
        )
        embeds[-1].add_field(
            name="mkc stats",
            value="```/mkc_stats team (stat) (season)```show the stats of everyone in a mkc roaster, the total average and the 6 best average, stat let you choose the type of stats (default is mmr), season let you choose the season to check the stats from (default to current season)",
            inline=False,
        )
        embeds[-1].add_field(
            name="fc stats",
            value="```/fc_stats room (team_size)```show the stats of a room using friend code, it need to be a room of 12 and while team_size is optionnal you should set it to have proper stats for each teams, room is where you paste your room info",
            inline=False,
        )
        embeds[-1].add_field(
            name="name history",
            value="```/name_history (player)```show the tracked name history with date of the selected player (you if player is not provided), and show when you will be able to change your name again",
            inline=False,
        )
        embeds[-1].add_field(
            name="lounge profile",
            value="```/lounge_profile (player)```show the lounge profile of the selected player (you if player is not provided)",
            inline=False,
        )

        embeds.append(
            discord.Embed(
                color=0x47E0FF,
                title="War stats commands",
                description="this section is about stats on played tracks in war, using <@177162177432649728> Quaxly will do stats on each tracks for you (each channel count as a different team and only people that have access to the channel can see the stats of the channel)",
            )
        )

        embeds[-1].add_field(
            name="war list",
            value="```/war list (channel)```show the list of recorded war with it's id for the selected channel (if no channel is provided it will use the current one)",
            inline=False,
        )
        embeds[-1].add_field(
            name="war delete",
            value="```/war delete (channel) (war_id)```let you delete a war (or all of them if you do not provide a war id), for the selected channel (or the current one if no channel is provided)",
            inline=False,
        )
        embeds[-1].add_field(
            name="war stats",
            value="```/war stats (channel) (minimum) (track)```show the stats for each track from best to worst in the selected channel (if no channel is provided it will use the current one), minimum is the minimum time a track need to be played to count in the stats it default to 1, track is an option to view stats from one track only",
            inline=False,
        )

        embeds.append(
            discord.Embed(
                color=0x47E0FF,
                title="War bot commands",
                description="this is a war bot implementation like sokuji",
            )
        )

        embeds[-1].add_field(
            name="war start",
            value="```/war start tag enemy_tag```start a war with selected teams",
            inline=False,
        )
        embeds[-1].add_field(
            name="war system",
            value="**1:** you are supposed to type the map abbreviation in the war channel when it gets picked\n\n**2:** type score all attached to each other in order (exemple: `134568`) to count a race\n**warning** bottom spots are added automatically so you never have to type 12 for exemple\n`-` is a range and if at the start can be used to specify the top spots (exemple: `-379` would be top3 7 9 and 12)\n\n**3:** misstyped something? Just type `back` and it will erase the last race\n\n**4:** want to add a track afterward? You can type `race <nb> <track>` to change it (example: `race 7 bdd`)",
            inline=False,
        )
        embeds[-1].add_field(
            name="war stop",
            value="```/war stop```stop the current war, you don't really have to type this if you do not usually type in the channel, war resets automatically if you start a new one and timeout after 3 hours",
            inline=False,
        )

        embeds[-1].add_field(
            name="this section is very new",
            value="if you need more information or my assistance my contact is on the last page",
            inline=False,
        )

        embeds.append(discord.Embed(color=0x47E0FF, title="Utility"))

        embeds[-1].add_field(
            name="tracks",
            value="```/tracks```show a message with all the cup in the game as button, pressing a button will show you the track name to use for the 4 tracks of the selected cup",
        )
        embeds[-1].add_field(
            name="debug",
            value="```/debug```show the bot debug info",
        )
        embeds[-1].add_field(
            name="lineup",
            value="```/lineup players time host enemy_tag tag```this command help to make a lineup ping with useful information and formating fast (it will ping users in the lineup with information)\n- `players`: you need to ping with @ the list of players (6 maximum)\n- `time`: the time this war is scheduled for (this now support unix timestamp like this `<t:1691154240:t>` that display as this <t:1691154240:t> with everyone local time)\n- `host`: you can set an FC or ping with an @ the host and the bot will display who it is and the fc, if it can't it will display your original input\n- `tags`: just the team names nothing special",
            inline=False,
        )
        embeds[-1].add_field(
            name="get in contact with me",
            value="if you want a new command, some improvement, a bug, or even just some questions I'll be happy to help you!\nhere's how to contact me:\n- discord: prrh (<@169497208406802432>)\n- support server: https://discord.gg/xucEGtxU9n\n- twitter: [@prismcmoi](https://twitter.com/prismcmoi)",
            inline=False,
        )

        await interaction.response.send_message(
            embed=embeds[0],
            view=Paginator(interaction=interaction, embeds=embeds),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
