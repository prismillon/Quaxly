import discord
import json

from discord import app_commands
from discord.ext import commands
from datetime import UTC, datetime
from utils import ConfirmButton, COLLATION
from statistics import mean
from cogs.war.base import Base
from autocomplete import mkc_tag_autocomplete, track_autocomplete
from database import get_db_session
from models import WarEvent, Race, GAME_MK8DX
from database import rs, r  # Keep Redis imports for overlay functionality

import utils


class WarStats(Base):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_toad_war = {}

        # Load cached wars from Redis (keep Redis for overlay functionality)
        cached_war = rs.keys("*")

        for war in cached_war:
            war_data = rs.get(war)
            war_data = json.loads(war_data)

            if "incoming_track" not in war_data:
                self.active_toad_war[int(war)] = war_data

    @commands.Cog.listener(name="on_message")
    async def toad_tracking(self, message: discord.Message):
        if message.author.id != 177162177432649728:
            return

        if "Started MK8DX 6v6" in message.content:
            extract_tag = message.content.replace("Started MK8DX 6v6: ", "")
            extract_tag = extract_tag[:-1].split(" vs ")
            tag = extract_tag[0]
            enemy_tag = extract_tag[1]
            date = datetime.now(UTC)

            # Create war event in PostgreSQL
            with get_db_session() as session:
                war_event = WarEvent(
                    game=GAME_MK8DX,
                    channel_id=message.channel.id,
                    date=date,
                    tag=tag,
                    enemy_tag=enemy_tag,
                )
                session.add(war_event)
                session.commit()

                # Prepare data for Redis (for overlay functionality)
                war_data = {
                    "id": war_event.id,
                    "channel_id": message.channel.id,
                    "date": date.isoformat(),
                    "tag": tag,
                    "enemy_tag": enemy_tag,
                    "home_score": [],
                    "enemy_score": [],
                    "spots": [],
                    "diff": [],
                    "tracks": [],
                }

                self.active_toad_war[message.channel.id] = war_data

                # Store in Redis for overlay
                await r.set(
                    message.channel.id,
                    json.dumps(war_data, default=str),
                )
            return

        if message.channel.id not in self.active_toad_war:
            return

        if "Stopped war." in message.content:
            if message.channel.id in self.active_toad_war:
                await r.delete(message.channel.id)
                self.active_toad_war.pop(message.channel.id)
            return

        if len(message.embeds) == 0:
            return

        race_data = message.embeds[0].to_dict()

        if "Score for Race" in race_data["title"]:
            spots = sorted(
                [int(spot[:-2]) for spot in race_data["fields"][0]["value"].split(", ")]
            )
            track = (
                race_data["fields"][4]["value"]
                if len(race_data["fields"]) == 5
                else "NULL"
            )
            diff = race_data["fields"][3]["value"]
            race_id = race_data["title"].replace("Score for Race ", "")

            war = self.active_toad_war[message.channel.id]
            war["spots"].append(spots)
            war["diff"].append(diff)
            war["tracks"].append(track)
            war["home_score"].append(41 + int(diff) / 2)
            war["enemy_score"].append(41 - int(diff) / 2)

            # Update PostgreSQL
            with get_db_session() as session:
                war_event = (
                    session.query(WarEvent).filter(WarEvent.id == war["id"]).first()
                )

                if war_event:
                    # Create new race record
                    race = Race(
                        war_event_id=war_event.id,
                        game=war_event.game,
                        race_number=len(war["spots"]),
                        track_name=track if track != "NULL" else None,
                        home_score=41 + int(diff) / 2,
                        enemy_score=41 - int(diff) / 2,
                        score_diff=int(diff),
                        positions=spots,
                    )
                    session.add(race)
                    session.commit()

            # Update Redis for overlay
            await r.set(
                message.channel.id,
                json.dumps(war, default=str),
            )

        elif "Total Score after Race" in race_data["title"]:
            race_id = int(race_data["title"].replace("Total Score after Race ", ""))
            war = self.active_toad_war[message.channel.id]

            # Truncate data to the specified race
            war["spots"] = war["spots"][:race_id]
            war["diff"] = war["diff"][:race_id]
            war["tracks"] = war["tracks"][:race_id]
            war["home_score"] = war["home_score"][:race_id]
            war["enemy_score"] = war["enemy_score"][:race_id]

            # Update PostgreSQL - remove races after the specified race
            with get_db_session() as session:
                war_event = (
                    session.query(WarEvent).filter(WarEvent.id == war["id"]).first()
                )

                if war_event:
                    # Delete races after the specified race_id
                    session.query(Race).filter(
                        Race.war_event_id == war_event.id, Race.race_number > race_id
                    ).delete()
                    session.commit()

            # Update Redis for overlay
            await r.set(
                message.channel.id,
                json.dumps(war, default=str),
            )

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(
        channel="the channel you want to check stats from",
        minimum="the minimum number of times the track has been played for it to count",
        track="the track you want to check stats from",
    )
    @app_commands.autocomplete(track=track_autocomplete, team=mkc_tag_autocomplete)
    async def stats(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,
        minimum: app_commands.Range[int, 1] = 1,
        track: str = None,
        team: str = None,
    ) -> None:
        """check race stats in the specified channel"""

        channel = channel or interaction.channel

        with get_db_session() as session:
            # Build query based on parameters
            query = session.query(WarEvent).filter(WarEvent.channel_id == channel.id)

            if team:
                query = query.filter(
                    (WarEvent.tag == team) | (WarEvent.enemy_tag == team)
                )

            war_events = query.all()

            if len(war_events) == 0:
                content = f"no stats registered in this channel"
                if team:
                    content += f" against the team {team}"
                return await interaction.response.send_message(
                    content=content,
                    ephemeral=True,
                )

            # Get race data
            track_stats = {}
            for war_event in war_events:
                for race in war_event.races:
                    if not race.track_name:
                        continue
                    if race.track_name not in track_stats:
                        track_stats[race.track_name] = []
                    track_stats[race.track_name].append(race.score_diff)

            # Filter by minimum occurrences
            track_stats = dict(
                filter(lambda x: len(x[1]) >= minimum, track_stats.items())
            )

            final_stats = {}
            for track_name, scores in track_stats.items():
                final_stats[track_name] = {
                    "average": round(mean(scores), 1),
                    "count": len(scores),
                    "best": max(scores),
                    "worst": min(scores),
                }

        if track:
            if track not in final_stats:
                return await interaction.response.send_message(
                    content=f"no stats for {track}", ephemeral=True
                )
            else:
                embed = discord.Embed(
                    color=0x47E0FF,
                    title=f"Statistics for {track} in {channel.name}",
                )
                data = final_stats[track]
                embed.add_field(name="Average", value=data["average"])
                embed.add_field(name="Count", value=data["count"])
                embed.add_field(name="Best", value=data["best"])
                embed.add_field(name="Worst", value=data["worst"])
                return await interaction.response.send_message(embed=embed)

        if not final_stats:
            return await interaction.response.send_message(
                content="no tracks with enough data", ephemeral=True
            )

        embed = discord.Embed(
            color=0x47E0FF,
            title=f"Statistics in {channel.name}",
        )

        # Sort by average (best first)
        sorted_stats = sorted(
            final_stats.items(), key=lambda x: x[1]["average"], reverse=True
        )

        description = "```\nTrack    | Avg  | Count | Best | Worst\n"
        description += "-" * 42 + "\n"

        for track_name, data in sorted_stats:
            description += f"{track_name:8} | {data['average']:4.1f} | {data['count']:5} | {data['best']:4} | {data['worst']:5}\n"

        description += "```"
        embed.description = description

        return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="list")
    @app_commands.guild_only()
    @app_commands.describe(channel="the channel you want to check wars from")
    async def warlist(
        self, interaction: discord.Interaction, channel: discord.TextChannel = None
    ):
        """list the most recent wars in the channel"""

        channel = channel or interaction.channel

        with get_db_session() as session:
            war_events = (
                session.query(WarEvent)
                .filter(WarEvent.channel_id == channel.id)
                .order_by(WarEvent.date.desc())
                .limit(10)
                .all()
            )

            if not war_events:
                return await interaction.response.send_message(
                    content="no wars found in this channel", ephemeral=True
                )

        embed = discord.Embed(
            color=0x47E0FF,
            title=f"Recent wars in {channel.name}",
        )

        for war_event in war_events:
            # Calculate total scores
            total_home_score = sum(race.home_score for race in war_event.races)
            total_enemy_score = sum(race.enemy_score for race in war_event.races)
            race_count = len(war_event.races)

            diff = total_home_score - total_enemy_score
            diff_str = f"{diff:+.1f}" if diff != 0 else "0.0"

            embed.add_field(
                name=f"{war_event.tag} vs {war_event.enemy_tag}",
                value=f"**{total_home_score:.1f} - {total_enemy_score:.1f}** ({diff_str}) | {race_count} races\nID: `{war_event.id}` | {war_event.date.strftime('%Y-%m-%d %H:%M')}",
                inline=False,
            )

        return await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(
        channel="the channel you want to delete war from",
        war_id="the id of the war you want to delete",
    )
    async def delete(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,
        war_id: str = None,
    ):
        """delete a war from the database"""

        channel = channel or interaction.channel

        if not war_id:
            return await interaction.response.send_message(
                content="please provide a war ID", ephemeral=True
            )

        try:
            war_id_int = int(war_id)
        except ValueError:
            return await interaction.response.send_message(
                content="invalid war ID format", ephemeral=True
            )

        with get_db_session() as session:
            war_event = (
                session.query(WarEvent)
                .filter(WarEvent.id == war_id_int, WarEvent.channel_id == channel.id)
                .first()
            )

            if not war_event:
                return await interaction.response.send_message(
                    content="war not found in this channel", ephemeral=True
                )

            embed = discord.Embed(
                color=0x47E0FF,
                title="Delete War",
                description=f"Are you sure you want to delete the war **{war_event.tag} vs {war_event.enemy_tag}**?\n"
                f"Date: {war_event.date.strftime('%Y-%m-%d %H:%M')}\n"
                f"Races: {len(war_event.races)}\n"
                f"ID: `{war_event.id}`",
            )

        view = ConfirmButton()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()

        if view.answer:
            with get_db_session() as session:
                # Re-fetch the war event in this session
                war_event = (
                    session.query(WarEvent).filter(WarEvent.id == war_id_int).first()
                )

                if war_event:
                    session.delete(war_event)  # Cascades to races
                    session.commit()

                    embed.title = "War Deleted"
                    embed.description = f"War **{war_event.tag} vs {war_event.enemy_tag}** has been deleted"
                else:
                    embed.title = "Error"
                    embed.description = "War not found"
        else:
            embed.title = "Action Canceled"
            embed.description = "War was not deleted"

        return await interaction.edit_original_response(embed=embed, view=None)
