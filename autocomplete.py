import copy
import discord
import os

from discord.app_commands import Choice
from typing import List
from utils import lounge_data, mkc_data
from db import db

TRACKS = db.Tracks.find({})


async def track_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    tcopy = copy.deepcopy(TRACKS)
    tracks = await tcopy.to_list(None)
    tracks = sorted(tracks, key=lambda x: x["id"])
    return [
        Choice(name=track["trackName"], value=track["trackName"])
        for track in tracks
        if track["trackName"].lower().startswith(current.lower())
    ][:25]


async def time_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
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
    return [
        Choice(name=player["name"], value=player["name"])
        for player in filter(
            lambda player: player["name"].lower().startswith(current.lower()),
            lounge_data.data(),
        )
    ][:25]


async def mkc_team_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    return [
        Choice(name=team["team_name"], value=str(team["team_name"]))
        for team in filter(
            lambda team: team["team_name"].lower().startswith(current.lower()),
            mkc_data.data(),
        )
    ][:25]


async def mkc_tag_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    return [
        Choice(name=team["team_name"], value=str(team["team_tag"]))
        for team in filter(
            lambda team: team["team_name"].lower().startswith(current.lower()),
            mkc_data.data(),
        )
    ][:25]


async def cmd_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[Choice[str]]:
    return [
        Choice(name=cmd.replace(".py", ""), value=f"cogs.{cmd.replace('.py', '')}")
        for cmd in filter(
            lambda cmd: cmd.lower().startswith(current.lower())
            and not cmd.startswith("__"),
            os.listdir(f"{os.path.dirname(__file__)}/cogs"),
        )
    ][:25]
