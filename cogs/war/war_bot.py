import discord
import json
import re

from datetime import datetime, timedelta, UTC
from discord.ext import commands, tasks
from discord import app_commands
from discord.app_commands import Range
from cogs.war.base import Base
from autocomplete import mkc_tag_autocomplete
from database import get_db_session
from models import WarEvent, Race, GAME_MK8DX
from database import rs, r  # Keep Redis imports for overlay functionality
from utils import COLLATION


_SCORE = (15, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)


def text_to_score(text: str):
    data = []
    prev = None
    next_list = []
    loopFlag = False
    while text:
        next_list = []
        if text.startswith("-"):
            loopFlag = True
            text = text[1:]
            if data:
                prev = data[-1]
            else:
                prev = 0
        if text.startswith("0"):
            next_list = [10]
            text = text[1:]
        elif text.startswith("+"):
            next_list = [11]
            text = text[1:]
        elif text.startswith("10"):
            next_list = [10]
            text = text[2:]
        elif text.startswith("110"):
            next_list = [1, 10]
            text = text[3:]
        elif text.startswith("1112"):
            next_list = [11, 12]
            text = text[4:]
        elif text.startswith("111"):
            next_list = [1, 11]
            text = text[3:]
        elif text.startswith("112"):
            next_list = [1, 12]
            text = text[3:]
        elif text.startswith("11"):
            next_list = [11]
            text = text[2:]
        elif text.startswith("12"):
            if data:
                next_list = [12]
            else:
                next_list = [1, 2]
            text = text[2:]
        elif text:
            next_list = [int(text[0], 16)]
            text = text[1:]
        if loopFlag:
            if not next_list:
                next_list = [12]
            next = next_list[0]
            while next - prev > 1:
                data.append(prev + 1)
                prev += 1
            loopFlag = False
        data += next_list
    return validate_score(set(data))


def validate_score(data: int):
    last_spot = 12
    while len(data) < 6:
        data.add(last_spot)
        last_spot -= 1
    return sorted(list(data))[:6]


def make_embed(war):
    embed = discord.Embed(
        color=0x47E0FF, title=f"Total Score after Race {len(war['diff'])}"
    )
    diff = sum(war["home_score"]) - sum(war["enemy_score"])
    embed.add_field(name=war["tag"], value=sum(war["home_score"]))
    embed.add_field(name=war["enemy_tag"], value=sum(war["enemy_score"]))
    embed.add_field(
        name="Difference",
        value=f"{diff if diff < 0 else '+' + str(diff)}",
        inline=False,
    )
    if len(war["diff"]) > 0:
        race_field_value = "```\n"
        for i, (spot, diff, track) in enumerate(
            zip(war["spots"], war["diff"], war["tracks"])
        ):
            diff = str(diff) if diff < 0 else "+" + str(diff)
            spot = re.sub("[\\[\\] ]", "", str(spot))
            race_field_value += f"{i + 1:2}: {diff:>3} | {spot:14} {'(' + track + ')' if track else ''}\n"
        race_field_value += "```"
        embed.add_field(name="Races", value=race_field_value, inline=False)
    return embed


class WarBot(Base):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_war = {}

        # Load cached wars from Redis (keep Redis for overlay functionality)
        cached_war = rs.keys("*")

        for war in cached_war:
            war_data = rs.get(war)
            war_data = json.loads(war_data)

            if "incoming_track" in war_data:
                self.active_war[int(war)] = war_data

        self._remove_war_task = self.remove_expired_war.start()

    @app_commands.command(name="start")
    @app_commands.guild_only()
    @app_commands.autocomplete(tag=mkc_tag_autocomplete, enemy_tag=mkc_tag_autocomplete)
    @app_commands.describe(
        tag="the tag of your team", enemy_tag="the tag of the enemy team"
    )
    async def warstart(
        self, interaction: discord.Interaction, tag: str, enemy_tag: str
    ):
        """start a war in the channel"""

        if not interaction.channel.permissions_for(interaction.guild.me).send_messages:
            return await interaction.response.send_message(
                content="missing send message permission in this channel, can't start war",
                ephemeral=True,
            )

        date = datetime.now(UTC)

        # Create war event in PostgreSQL
        with get_db_session() as session:
            war_event = WarEvent(
                game=GAME_MK8DX,  # Default to MK8DX for compatibility
                channel_id=interaction.channel.id,
                date=date,
                tag=tag,
                enemy_tag=enemy_tag,
                incoming_track=None,
            )
            session.add(war_event)
            session.commit()

            # Prepare data for Redis (for overlay functionality)
            war_data = {
                "id": war_event.id,
                "channel_id": interaction.channel.id,
                "date": date.isoformat(),
                "tag": tag,
                "enemy_tag": enemy_tag,
                "home_score": [],
                "enemy_score": [],
                "spots": [],
                "diff": [],
                "tracks": [],
                "incoming_track": None,
            }

            self.active_war[interaction.channel.id] = war_data

            # Store in Redis for overlay
            await r.set(
                interaction.channel.id,
                json.dumps(war_data, default=str),
            )

        return await interaction.response.send_message(
            f"started war between `{tag}` and `{enemy_tag}` \n(obs overlay: https://waroverlay.prismillon.com/overlay/{interaction.channel.id})"
        )

    @app_commands.command(name="stop")
    @app_commands.guild_only()
    async def warstop(self, interaction: discord.Interaction):
        """stop the war"""

        if interaction.channel.id in self.active_war:
            await r.delete(interaction.channel.id)
            self.active_war.pop(interaction.channel.id)
            return await interaction.response.send_message("stopped war")
        await interaction.response.send_message("no active war")

    @app_commands.command(name="edit_race")
    @app_commands.guild_only()
    @app_commands.describe(race_nb="the race number", spots="the new spots")
    async def edit_race(
        self, interaction: discord.Interaction, race_nb: Range[int, 1], spots: str
    ):
        """edit a race number spots"""
        if interaction.channel.id not in self.active_war:
            return await interaction.response.send_message(
                content="no active war", ephemeral=True
            )

        war = self.active_war[interaction.channel.id]

        if len(war["spots"]) < race_nb:
            return await interaction.response.send_message(
                content="invalid race number", ephemeral=True
            )

        if not re.fullmatch("^((?!--)[0-9+-])+$", spots):
            return await interaction.response.send_message(
                content="invalid spots format", ephemeral=True
            )

        new_spots = text_to_score(spots)
        war["spots"][race_nb - 1] = new_spots
        new_diff = sum(_SCORE[spot - 1] for spot in new_spots) - 41
        war["diff"][race_nb - 1] = new_diff
        war["home_score"][race_nb - 1] = 41 + new_diff / 2
        war["enemy_score"][race_nb - 1] = 41 - new_diff / 2

        # Update PostgreSQL
        with get_db_session() as session:
            # Find the war event
            war_event = session.query(WarEvent).filter(WarEvent.id == war["id"]).first()

            if war_event:
                # Find the specific race
                race = (
                    session.query(Race)
                    .filter(
                        Race.war_event_id == war_event.id, Race.race_number == race_nb
                    )
                    .first()
                )

                if race:
                    race.positions = new_spots
                    race.score_diff = new_diff
                    race.home_score = 41 + new_diff / 2
                    race.enemy_score = 41 - new_diff / 2
                    session.commit()

        # Update Redis for overlay
        await r.set(interaction.channel.id, json.dumps(war, default=str))

        embed = make_embed(war)
        return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="track")
    @app_commands.guild_only()
    @app_commands.describe(track="the track")
    async def incoming_track(self, interaction: discord.Interaction, track: str = None):
        """set or remove the next track"""

        if interaction.channel.id not in self.active_war:
            return await interaction.response.send_message(
                content="no active war", ephemeral=True
            )

        war = self.active_war[interaction.channel.id]
        war["incoming_track"] = track

        # Update PostgreSQL
        with get_db_session() as session:
            war_event = session.query(WarEvent).filter(WarEvent.id == war["id"]).first()

            if war_event:
                war_event.incoming_track = track
                session.commit()

        # Update Redis for overlay
        await r.set(interaction.channel.id, json.dumps(war, default=str))

        if track:
            return await interaction.response.send_message(f"next track: `{track}`")
        else:
            return await interaction.response.send_message("removed next track")

    @tasks.loop(minutes=1)
    async def remove_expired_war(self):
        expired_date = datetime.now(UTC) - timedelta(hours=6)
        to_remove = []
        for channel_id, war in self.active_war.items():
            war_date = datetime.fromisoformat(war["date"])
            if war_date < expired_date:
                to_remove.append(channel_id)
        for channel_id in to_remove:
            await r.delete(channel_id)
            self.active_war.pop(channel_id)

    @commands.Cog.listener(name="on_message")
    async def war_score(self, message: discord.Message):
        if message.channel.id not in self.active_war:
            return

        if not re.fullmatch("^((?!--)[0-9+-])+$", message.content):
            return

        war = self.active_war[message.channel.id]
        positions = text_to_score(message.content)
        diff = sum(_SCORE[position - 1] for position in positions) - 41
        home_score = 41 + diff / 2
        enemy_score = 41 - diff / 2

        war["spots"].append(positions)
        war["diff"].append(diff)
        war["tracks"].append(war["incoming_track"])
        war["home_score"].append(home_score)
        war["enemy_score"].append(enemy_score)
        war["incoming_track"] = None

        # Update PostgreSQL
        with get_db_session() as session:
            war_event = session.query(WarEvent).filter(WarEvent.id == war["id"]).first()

            if war_event:
                # Create new race record
                race = Race(
                    war_event_id=war_event.id,
                    game=war_event.game,
                    race_number=len(war["spots"]),
                    track_name=war["tracks"][-1],
                    home_score=home_score,
                    enemy_score=enemy_score,
                    score_diff=diff,
                    positions=positions,
                )
                session.add(race)

                # Clear incoming track
                war_event.incoming_track = None
                session.commit()

        # Update Redis for overlay
        await r.set(message.channel.id, json.dumps(war, default=str))

        embed = make_embed(war)
        return await message.channel.send(embed=embed)
