import asyncio
import sqlite3
from motor.motor_asyncio import AsyncIOMotorClient
import os


async def get_pool():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    db = client["quaxly"]
    return db


conn = sqlite3.connect("mk.db")
cursor = conn.cursor()


async def transfer_full_users(db):
    cursor.execute("SELECT discordId FROM Users")
    user_data = cursor.fetchall()
    categories = ["Ni150", "Sh150", "Ni200", "Sh200"]

    users = db.Users

    async def process_user(user_data):
        user = {
            "discordId": user_data[0],
            "servers": [],
            "ni150Tracks": [],
            "sh150Tracks": [],
            "ni200Tracks": [],
            "sh200Tracks": [],
        }
        cursor.execute("SELECT discordId, serverId FROM Servers WHERE discordId = ?", (user_data[0],))
        servers_data = cursor.fetchall()
        for server in servers_data:
            user["servers"].append({"serverId": server[1]})
        for category in categories:
            cursor.execute(f"SELECT discordId, trackName, time FROM {category} WHERE discordId = ?", (user_data[0],))
            tracks_data = cursor.fetchall()
            for track in tracks_data:
                ref = await db.Tracks.find_one({"trackName": track[1]})
                user[f"{category.lower()}Tracks"].append({
                    "trackRef": ref["_id"],
                    "time": track[2],
                })
        await users.insert_one(user)

    tasks = [process_user(user) for user in user_data]
    print("Process user")
    await asyncio.gather(*tasks)
    print("Process user FINISH")


async def transfer_cups_and_tracks(db):
    cursor.execute("SELECT id, cupName, cupEmojiName, cupEmojiId, cupUrl FROM Cups")
    cups_data = cursor.fetchall()

    cups = db.Cups
    tracks = db.Tracks
    collation = {"locale": "en", "strength": 1}
    await tracks.create_index([("trackName", 1)], collation=collation)

    async def process_cup(cup):
        cup_data = {
            "id": cup[0],
            "cupName": cup[1],
            "cupEmojiName": cup[2],
            "cupEmojiId": cup[3],
            "cupUrl": cup[4],
            "tracks": [],
        }
        cup_id = await cups.insert_one(cup_data)

        cursor.execute(f"SELECT id, trackName, cupId, trackUrl, fullName FROM Tracks WHERE cupId = {cup[0]}")
        tracks_data = cursor.fetchall()

        for track in tracks_data:
            track_data = {
                "id": track[0],
                "trackName": track[1],
                "cupId": cup_id.inserted_id,
                "trackUrl": track[3],
                "fullName": track[4],
            }
            track_id = await tracks.insert_one(track_data)
            await cups.find_one_and_update(
                {"_id": cup_id.inserted_id},
                {"$push": {"tracks": track_id.inserted_id}},
            )

    tasks = [process_cup(cup) for cup in cups_data]
    print("Process cup")
    await asyncio.gather(*tasks)
    print("Process cup FINISH")


async def transfer_wars(db):
    cursor.execute("SELECT id, channelId, date, tag, ennemyTag FROM Wars")
    wars_data = cursor.fetchall()

    wars = db.Wars

    async def process_war(war):
        cursor.execute(
            f"SELECT id, warId, track, diff, spot1, spot2, spot3, spot4, spot5, spot6 FROM Races WHERE warId = {war[0]}")
        races_data = cursor.fetchall()
        home_score = []
        enemy_score = []
        spots = []
        diff = []
        tracks = []
        for track in races_data:
            spots.append([track[4], track[5], track[6], track[7], track[8], track[9]])
            diff.append(track[3])
            if track[2] != "NULL":
                tracks.append(track[2])
            else:
                tracks.append(None)
            home_score.append(diff[-1] / 2 + 41)
            enemy_score.append(82 - home_score[-1])
        war_data = {
            "channel_id": war[1],
            "date": war[2],
            "tag": war[3],
            "enemy_tag": war[4],
            "home_score": home_score,
            "enemy_score": enemy_score,
            "spots": spots,
            "diff": diff,
            "tracks": tracks,
        }
        await wars.insert_one(war_data)

    tasks = [process_war(war) for war in wars_data]
    print("Process war")
    await asyncio.gather(*tasks)
    print("Process war FINISH")


async def transfer_data(db):
    await asyncio.gather(transfer_cups_and_tracks(db))
    await asyncio.gather(transfer_full_users(db))
    await asyncio.gather(transfer_wars(db))


async def main():
    db = await get_pool()
    await transfer_data(db)
    db.client.close()


if __name__ == "__main__":
    asyncio.run(main())
