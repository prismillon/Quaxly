import discord
import pymongo
import os
import copy

client = pymongo.MongoClient(os.getenv('MONGODB_URL'))
db = client.quaxly

last_96_documents = db.Tracks.find().sort('_id', -1).limit(96)

for doc in last_96_documents:
    db.Tracks.delete_one({'_id': doc['_id']})

db.Tracks.update_one({'trackName': 'bPPC'}, {"$set": {"fullName": "Piranha Plant Cove"}})

tracks = db.Tracks.find({})

wars = db.Wars.find({})

for war in list(wars):
  new_tracks = []
  for track in war['tracks']:
    if discord.utils.find(lambda t: t['fullName'] == track, copy.deepcopy(tracks)):
      track_name = discord.utils.find(lambda t: t['fullName'] == track, copy.deepcopy(tracks))['trackName']
      new_tracks.append(track_name)
    else:
      new_tracks.append(track)
  
  db.Wars.update_one({'_id': war['_id']}, {"$set": {"tracks": new_tracks}})
  print(f"Updated tracks for war {war['_id']}", end='\r')