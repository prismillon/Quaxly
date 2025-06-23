import copy
import discord
import os

from discord.app_commands import Choice
from typing import List
from utils import lounge_data, mkc_data
from database import get_db_session
from models import Track, GAME_MK8DX


async def track_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    """Autocomplete for MK8DX track names (for compatibility with existing commands)"""
    with get_db_session() as session:
        tracks = (
            session.query(Track)
            .filter(Track.game == GAME_MK8DX)
            .order_by(Track.track_id)
            .all()
        )

        filtered_tracks = [
            track
            for track in tracks
            if track.track_name.lower().startswith(current.lower())
        ][:25]

        return [
            Choice(name=track.track_name, value=track.track_name)
            for track in filtered_tracks
        ]


async def time_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    """Time format autocomplete helper"""
    if len(current) == 0:
        return [Choice(name="Format: 1:23.456", value="Format: 1:23.456")]
    elif len(current) == 6:
        current = current[:1] + ":" + current[1:3] + "." + current[3:]
        return [Choice(name=current, value=current)]
    elif len(current) == 8:
        current = current[:1] + ":" + current[2:4] + "." + current[5:]
        return [Choice(name=current, value=current)]
    else:
        return [Choice(name=current, value=current)]


async def name_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    """Lounge player name autocomplete"""
    if not current:
        return []

    players = await lounge_data.search_players(search=current, limit=25)
    if not players:
        return []

    return [
        Choice(name=player["name"], value=player["name"])
        for player in players
        if player.get("name", "").lower().startswith(current.lower())
    ][:25]


async def mkc_team_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    """MKC team name autocomplete"""
    if not current:
        return []

    teams = await mkc_data.search_teams(search=current, limit=25)
    if not teams:
        return []

    return [
        Choice(name=team["name"], value=team["name"])
        for team in teams
        if team.get("name", "").lower().startswith(current.lower())
    ][:25]


async def mkc_tag_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    """MKC team tag autocomplete"""
    if not current:
        return []

    teams = await mkc_data.search_teams(search=current, limit=25)
    if not teams:
        return []

    return [
        Choice(name=team["name"], value=team["tag"])
        for team in teams
        if team.get("name", "").lower().startswith(current.lower()) and team.get("tag")
    ][:25]


async def cmd_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    """Command autocomplete for extension management"""
    return [
        Choice(name=cmd.replace(".py", ""), value=f"cogs.{cmd.replace('.py', '')}")
        for cmd in filter(
            lambda cmd: cmd.lower().startswith(current.lower())
            and not cmd.startswith("__"),
            os.listdir(f"{os.path.dirname(__file__)}/cogs"),
        )
    ][:25]
