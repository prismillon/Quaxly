from neo4j import GraphDatabase
from pymongo import MongoClient

# Requête, renvois les courses pas faite par l'utilisateur
# match (u:User WHERE u.discordId = "916164345057120367"),(t:Track) WHERE NOT (u)-[:HAS_TRACK]->(t) return t
# match (u:User WHERE u.discordId = "916164345057120367"),(t:Track WHERE category = "ni150Tracks") WHERE NOT (u)-[:HAS_TRACK]->(t) return t
# Fonction pour se connecter à la base de données Neo4j
def get_neo4j_connection():
    driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "rootroot"))
    return driver

# Fonction pour se connecter à la base de données MongoDB
def get_mongo_connection():
    client = MongoClient("mongodb://localhost:27017")
    db = client["quaxly"]
    return db

def transfer_server(neo4j_session, mongo_db):
    users_collection = mongo_db.Users
    servers_id=[]
    session = neo4j_session.session()
    for user in users_collection.find():
        for server in user["servers"]:
            servers_id.append(str(server["serverId"]))
    for server_id in set(servers_id):
        server_node = {
            "serverId": str(server_id)
        }
        session.run(
                "CREATE (u:Server $server)", server=server_node
            )
    return

def transfer_war(neo4j_session, mongo_db):
    wars_collection = mongo_db.Wars
    # servers_id=[]
    session = neo4j_session.session()
    for war in wars_collection.find():
        if war["tag"] == "random":
            continue
        war_node = {
            "id": str(war["_id"]),
            "channelId": str(war["channel_id"]),
            "home_tag": war["tag"],
            "enemy_tag": war["ennemy_tag"]
        }
        session.run(
                "CREATE (u:War $war)", war=war_node
            )
        
        for index,track in enumerate(war["tracks"]):
            if track == "null":
                continue
            session.run(
                "MATCH (w:War), (t:Track) WHERE w.id = $id AND t.fullName = $fullName CREATE (w)-[:RACE { diff: $diff } ]->(t)",
                id=str(war["_id"]),
                fullName=track,
                diff=war["diff"][index]
            )
    return

def transfer_users(neo4j_session, mongo_db):
    users_collection = mongo_db.Users
    session = neo4j_session.session()
    for user in users_collection.find():
        #print(user["servers"])

        user_node = {
            "discordId": str(user["discordId"]),
            #"servers": user["servers"],
            # "ni150Tracks": user["ni150Tracks"],
            # "sh150Tracks": user["sh150Tracks"],
            # "ni200Tracks": user["ni200Tracks"],
            # "sh200Tracks": user["sh200Tracks"],
        }
        # Don't take false user
        if len(user["servers"]) == 0 and  len(user["ni150Tracks"]) == 0 and len(user["sh150Tracks"]) == 0 and len(user["ni200Tracks"]) == 0 and len(user["sh200Tracks"]) == 0:
            continue
        
        session.run(
            "CREATE (u:User $user_node)", user_node=user_node
        )

        for server in user["servers"]:
            session.run(
                "MATCH (c:User), (s:Server) WHERE c.discordId = $user_id AND s.serverId = $server_id CREATE (c)-[:MEMBER_OF ]->(s)",
                user_id=str(user["discordId"]),
                server_id=str(server["serverId"]),
            )
        categories = ["ni150Tracks", "sh150Tracks", "ni200Tracks", "sh200Tracks"]
        index=0
        for category in [user["ni150Tracks"],user["sh150Tracks"],user["ni200Tracks"],user["sh200Tracks"]]:
            for track in category:
                #print("MATCH (c:User WHERE c.discordId = \"" + str(user["discordId"]) + "\"), (t:Track WHERE t.trackId = \"" + str(track["trackRef"]) + "\") CREATE (c)-[:HAS_TRACK { time: "+ track["time"] +"}]->(t)")
                session.run(
                    "MATCH (c:User WHERE c.discordId = $user_id), (t:Track WHERE t.trackId = $track_id) CREATE (c)-[:HAS_TRACK { time: '$time', category: $category}]->(t)",
                    user_id=str(user["discordId"]),
                    track_id=str(track["trackRef"]),
                    time=track["time"],
                    category=categories[index]
                )
            index += 1
        # for sh150 in user["sh150Tracks"]:
        #     session.run(
        #         "MATCH (c:User), (t:Track) WHERE c.discordId = $user_id AND t.id = $track_id CREATE (c)-[:HAS_TRACK { time: $time}]->(t)",
        #         user_id=user["discordId"],
        #         track_ref=ni150["trackRef"],
        #         time=ni150["time"]
        #     )

def transfer_tracks(neo4j_session,mongo_db):
    mongo_tracks = mongo_db.Tracks
    session = neo4j_session.session()
    for track in mongo_tracks.find():
        track_node = {
            "trackId": str(track["_id"]),
            "trackName": track["trackName"],
            "fullName": track["fullName"],
        }
        session.run(
                "CREATE (u:Track $track)", track=track_node
        )

def main():
    neo4j_session = get_neo4j_connection()
    mongo_db = get_mongo_connection()
    transfer_server(neo4j_session,mongo_db)
    transfer_tracks(neo4j_session,mongo_db)
    transfer_war(neo4j_session,mongo_db)
    transfer_users(neo4j_session,mongo_db)

    neo4j_session.close()
    mongo_db.client.close()

if __name__ == "__main__":
    main()
