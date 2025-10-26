import os
from typing import List

import discord
from discord.app_commands import Choice

from database import get_db_session
from models import GAME_MK8DX, Track
from utils import lounge_data, mkc_data


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

    rosters = await mkc_data.search_teams(search=current, limit=25)
    if not rosters:
        return []

    choices = []
    for roster in rosters:
        team_name = roster.get("team_name", "")
        if team_name and team_name.lower().startswith(current.lower()):
            choices.append(
                Choice(
                    name=f"{team_name} ({roster.get('game', '')})",
                    value=f"{roster.get('team_id')}-{roster.get('id')}",
                )
            )
    return choices[:25]


async def mkc_tag_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    """MKC team tag autocomplete"""
    if not current:
        return []

    rosters = await mkc_data.search_teams(search=current, limit=25)
    if not rosters:
        return []

    # Group by team name to avoid duplicates
    seen_teams = set()
    choices = []
    for roster in rosters:
        team_name = roster.get("team_name", "")
        tag = roster.get("tag")
        if (
            team_name
            and tag
            and team_name not in seen_teams
            and team_name.lower().startswith(current.lower())
        ):
            seen_teams.add(team_name)
            choices.append(Choice(name=team_name, value=tag))
    return choices[:25]


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
