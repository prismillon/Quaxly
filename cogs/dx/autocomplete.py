import discord
from discord import app_commands
from database import get_db_session
from models import Track, TimeRecord, User, GAME_MK8DX
from game_utils import get_game_tracks


async def dx_track_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """Autocomplete for MK8DX track names"""
    with get_db_session() as session:
        tracks = get_game_tracks(session, GAME_MK8DX)

        if current:
            filtered_tracks = [
                track
                for track in tracks
                if current.lower() in track.track_name.lower()
                or current.lower() in track.full_name.lower()
            ]
        else:
            filtered_tracks = tracks

        filtered_tracks = sorted(filtered_tracks, key=lambda x: x.track_id)[:25]

        return [
            app_commands.Choice(
                name=f"{track.track_name} - {track.full_name}", value=track.track_name
            )
            for track in filtered_tracks
        ]


async def dx_time_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """Autocomplete for time format examples"""
    examples = ["1:23.456", "2:15.789", "1:45.123", "2:30.000", "1:59.999"]

    if current:
        if len(current) == 1 and current.isdigit():
            return [
                app_commands.Choice(name=f"{current}:00.000", value=f"{current}:00.000")
            ]
        elif ":" in current and "." not in current:
            return [app_commands.Choice(name=f"{current}.000", value=f"{current}.000")]
        else:
            filtered = [ex for ex in examples if ex.startswith(current)]
            return [app_commands.Choice(name=ex, value=ex) for ex in filtered[:5]]

    return [app_commands.Choice(name=ex, value=ex) for ex in examples[:5]]
