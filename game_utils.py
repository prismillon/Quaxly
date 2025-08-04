from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from database import get_db_session
from models import (
    VALID_GAMES,
    Cup,
    Race,
    TimeRecord,
    Track,
    User,
    WarEvent,
    get_leaderboard,
)


def validate_game(game: str) -> str:
    """Validate and normalize game identifier"""
    game = game.lower()
    if game not in VALID_GAMES:
        raise ValueError(
            f"Invalid game '{game}'. Valid games: {', '.join(VALID_GAMES)}"
        )
    return game


def get_game_cups(session: Session, game: str) -> List[Cup]:
    """Get all cups for a specific game"""
    game = validate_game(game)
    return session.query(Cup).filter(Cup.game == game).order_by(Cup.id).all()


def get_game_tracks(
    session: Session, game: str, cup_id: Optional[int] = None
) -> List[Track]:
    """Get all tracks for a specific game, optionally filtered by cup"""
    game = validate_game(game)
    query = session.query(Track).filter(Track.game == game)

    if cup_id is not None:
        query = query.filter(Track.cup_id == cup_id)

    return query.order_by(Track.track_id).all()


def get_track_by_name(session: Session, game: str, track_name: str) -> Optional[Track]:
    """Get a track by its short name within a specific game"""
    game = validate_game(game)
    return (
        session.query(Track)
        .filter(Track.game == game, Track.track_name.ilike(track_name))
        .first()
    )


def get_track_by_id(session: Session, game: str, track_id: int) -> Optional[Track]:
    """Get a track by its ID within a specific game"""
    game = validate_game(game)
    return (
        session.query(Track)
        .filter(Track.game == game, Track.track_id == track_id)
        .first()
    )


def get_user_times_for_game(
    session: Session, user_id: int, game: str
) -> List[TimeRecord]:
    """Get all time records for a user in a specific game"""
    game = validate_game(game)
    return (
        session.query(TimeRecord)
        .filter(TimeRecord.user_id == user_id, TimeRecord.game == game)
        .order_by(TimeRecord.time_milliseconds)
        .all()
    )


def get_game_leaderboard(
    session: Session,
    game: str,
    track_name: str,
    race_type: str,
    speed: int,
    limit: Optional[int] = None,
) -> List[TimeRecord]:
    """Get leaderboard for a specific track in a specific game"""
    game = validate_game(game)
    track = get_track_by_name(session, game, track_name)
    if not track:
        return []

    return get_leaderboard(session, track.id, game, race_type, speed, limit)


def get_game_wars(
    session: Session, game: str, limit: Optional[int] = None
) -> List[WarEvent]:
    """Get war events for a specific game"""
    game = validate_game(game)
    query = (
        session.query(WarEvent)
        .filter(WarEvent.game == game)
        .order_by(WarEvent.date.desc())
    )

    if limit:
        query = query.limit(limit)

    return query.all()


def get_game_stats(session: Session, game: str) -> Dict[str, Any]:
    """Get statistics for a specific game"""
    game = validate_game(game)

    stats = {
        "game": game.upper(),
        "cups": session.query(Cup).filter(Cup.game == game).count(),
        "tracks": session.query(Track).filter(Track.game == game).count(),
        "time_records": session.query(TimeRecord)
        .filter(TimeRecord.game == game)
        .count(),
        "war_events": session.query(WarEvent).filter(WarEvent.game == game).count(),
        "races": session.query(Race).filter(Race.game == game).count(),
    }

    unique_users = (
        session.query(TimeRecord.user_id)
        .filter(TimeRecord.game == game)
        .distinct()
        .count()
    )
    stats["active_users"] = unique_users

    return stats


def get_all_games_stats(session: Session) -> Dict[str, Dict[str, Any]]:
    """Get statistics for all games"""
    all_stats = {}

    for game in VALID_GAMES:
        all_stats[game] = get_game_stats(session, game)

    all_stats["total"] = {
        "users": session.query(User).count(),
        "total_time_records": session.query(TimeRecord).count(),
        "total_war_events": session.query(WarEvent).count(),
        "total_races": session.query(Race).count(),
    }

    return all_stats


def print_game_stats(game: Optional[str] = None):
    """Print statistics for a specific game or all games"""
    with get_db_session() as session:
        if game:
            game = validate_game(game)
            stats = get_game_stats(session, game)
            print(f"\n{stats['game']} Statistics:")
            print("=" * 30)
            print(f"Cups: {stats['cups']}")
            print(f"Tracks: {stats['tracks']}")
            print(f"Time Records: {stats['time_records']}")
            print(f"Active Users: {stats['active_users']}")
            print(f"War Events: {stats['war_events']}")
            print(f"Races: {stats['races']}")
        else:
            all_stats = get_all_games_stats(session)
            print("\nDatabase Statistics by Game:")
            print("=" * 40)

            for game_key, stats in all_stats.items():
                if game_key == "total":
                    continue
                print(f"\n{stats['game']}:")
                print(f"  Cups: {stats['cups']}")
                print(f"  Tracks: {stats['tracks']}")
                print(f"  Time Records: {stats['time_records']}")
                print(f"  Active Users: {stats['active_users']}")
                print(f"  War Events: {stats['war_events']}")
                print(f"  Races: {stats['races']}")

            print("\nOverall Totals:")
            print(f"  Total Users: {all_stats['total']['users']}")
            print(f"  Total Time Records: {all_stats['total']['total_time_records']}")
            print(f"  Total War Events: {all_stats['total']['total_war_events']}")
            print(f"  Total Races: {all_stats['total']['total_races']}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        game_arg = sys.argv[1]
        try:
            print_game_stats(game_arg)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print_game_stats()
