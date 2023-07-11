from .display_time import display_time
from .register import register_user, remove_user
from .manage_time import save_time, delete_time
from .tracks import tracks
from .lineup import lineup
from .name_history import name_history
from .team_stats import role_stats, mkc_stats

commands = [
    display_time,
    register_user,
    remove_user,
    save_time,
    delete_time,
    tracks,
    lineup,
    name_history,
    role_stats,
    mkc_stats
]