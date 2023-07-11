import sqlite3
import discord

con = sqlite3.connect("mk.db", check_same_thread=False)
db = con.cursor()

#get

def get_best_times(mode, guild_id):
    times = db.execute(f"""SELECT A.trackName, A.time, A.discordId
                FROM {mode} AS A
                JOIN Servers ON Servers.discordId = A.discordId
                JOIN Tracks AS t ON t.trackName = A.trackName
                WHERE Servers.serverId = ?
                GROUP BY A.trackName
                HAVING A.time = MIN(A.time)
                ORDER BY t.id""", (guild_id,))
    return times.fetchall()

def get_player_best(mode, guild_id, player_id):
    times = db.execute(f"""SELECT A.trackName, A.time, Position,Total_players
                FROM (SELECT mode.trackName, mode.time as time FROM {mode} as mode
                    JOIN Servers ON Servers.discordId = mode.discordId
                    WHERE mode.discordId = ? AND Servers.serverId = ?
                    ORDER BY mode.trackName) as A
                JOIN (SELECT trackName,COUNT(*) as Total_players FROM {mode} as mode
                    JOIN Servers ON mode.discordId = Servers.discordId
                    WHERE Servers.serverId = ?
                    GROUP BY trackName) as B ON A.trackName = B.trackName
                JOIN (SELECT mode.trackName, COUNT(*) as Position FROM {mode} as mode
                    JOIN Servers ON mode.discordId = Servers.discordId
                    JOIN (SELECT mode.trackName, mode.time as user_time FROM {mode} as mode
                            JOIN Servers ON Servers.discordId = mode.discordId
                            WHERE mode.discordId = ? AND Servers.serverId = ?) as A ON A.trackName = mode.trackName
                    WHERE (mode.time < A.user_time OR mode.discordId = ?) AND Servers.serverId = ?
                    GROUP BY mode.trackName) as C ON A.trackName = C.trackName
                JOIN Tracks ON Tracks.trackName = A.trackName
                ORDER BY id""", (player_id, guild_id, guild_id, player_id, guild_id, player_id, guild_id))
    return times.fetchall()

def get_track_times(mode, guild_id, track):
    times = db.execute(f"""select mode.discordId, mode.time, mode.trackName, Tracks.trackUrl from {mode} as mode 
                JOIN Servers ON mode.discordId = Servers.discordId 
                JOIN Tracks on mode.trackName = Tracks.trackName
                WHERE serverId = ? and mode.trackName like ?
                ORDER BY time""", (guild_id, track))
    return times.fetchall()

def get_user_track_time(mode, guild_id, track, player_id):
    times = db.execute(f"""select mode.discordId, mode.trackName, mode.time, t.trackUrl from {mode} as mode
                join Tracks as t on mode.trackName = t.trackName
                join Servers as s on mode.discordId = s.discordId
                where mode.trackName like ? and mode.discordId = ? and s.serverId = ?
                """, (track, player_id, guild_id))
    return times.fetchall()

def get_track_names(current):
    return db.execute("select trackName from Tracks where trackName like ? ORDER BY id limit 25", (current+'%',))

def get_user_times(mode, player_id, track):
    return db.execute(f"select mode.trackName, time from {mode} as mode join Tracks on mode.trackName = Tracks.trackName where discordId = ? and mode.trackName like ? order by Tracks.id", (player_id, track)).fetchall()

def get_cups_emoji():
    return db.execute("select cupEmojiName, cupEmojiId from Cups").fetchall()

def get_tracks_from_cup(cup_name):
    return db.execute("select trackName, cupName, cupUrl from Tracks JOIN Cups ON Tracks.cupId = Cups.id where cupEmojiName = ?", (cup_name,)).fetchall()

def get_all_users_from_server(guild_id):
    return db.execute("select discordId from Servers where serverId = ?", (guild_id,)).fetchall()

#check

def check_track_name(track):
    return db.execute("select trackName, trackUrl from tracks where trackName like ?", (track,)).fetchall()

def check_player_server(player_id, guild_id):
    return db.execute("select discordId from Servers where discordId = ? and serverId = ?", (player_id, guild_id)).fetchall()

def check_player(player_id):
    return db.execute("select discordId from Users where discordId = ?", (player_id,)).fetchall()

#delete

def delete_player_from_server(player_id, guild_id):
    db.execute("delete from Servers where discordId = ? and serverId = ?", (player_id, guild_id))
    con.commit()

def delete_player_times(mode, player_id, track):
    db.execute(f"delete from {mode} where discordId = ? and trackName like ?", (player_id, track))
    con.commit()

#add

def register_new_player(player_id):
    db.execute("insert into Users (discordId) values(?)", (player_id,))
    con.commit()

def register_user_in_server(player_id, guild_id):
    db.execute("insert into Servers (serverId, discordId) values(?, ?)", (guild_id, player_id))
    con.commit()

def save_time(mode, player_id, track, time):
    db.execute(f"insert into {mode} (trackName, discordId, time) values(?, ?, ?)", (track, player_id, time))
    con.commit()

#update

def update_time(mode, player_id, track, time):
    db.execute(f"update {mode} set time = ? where trackName = ? and discordId = ?", (time, track, player_id))
    con.commit()