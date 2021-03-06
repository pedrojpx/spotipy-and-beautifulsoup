import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from datetime import datetime
from json.decoder import JSONDecodeError
from spotipy.oauth2 import SpotifyClientCredentials
from pymongo import MongoClient

playlist_id = "4mKsMyOuYluG5XiUSpNClb" #sys.argv[1] # exemplo "4mKsMyOuYluG5XiUSpNClb"
playlist_tracks = []
playlist_track_ids = []

#Autenticação depende de variaveis de ambiente:
#SPOTIPY_CLIENT_ID
#SPOTIPY_CLIENT_SECRET
#SPOTIPY_REDIRECT_URI
spotify = spotipy.Spotify(auth_manager = SpotifyClientCredentials())

tracks_from_api = spotify.playlist(playlist_id, fields="name,tracks")#search(q="name:Mixolydian", type='playlist')

for item in tracks_from_api['tracks']['items']:
    trackObject = {}
    trackObject['track_id'] = item['track']['id']
    trackObject['name'] = item['track']['name']
    trackObject['artists'] = item['track']['artists'] # TO-DO: limpar os dados inúteis
    trackObject['genres'] = '' #info not in this object
    trackObject['explicit'] = item['track']['explicit']
    trackObject['last_analyzed'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    trackObject['key'] = '' #info not in this object
    trackObject['mode'] = '' #info not in this object
    trackObject['time_signature'] = '' #info not in this object
    trackObject['tempo'] = '' #info not in this object
    trackObject['instrumentalness'] = '' #info not in this object
    trackObject['speechiness'] = '' #info not in this object
    trackObject['acousticness'] = '' #info not in this object
    trackObject['energy'] = '' #info not in this object
    trackObject['danceability'] = '' #info not in this object
    trackObject['valence'] = '' #info not in this object
    trackObject['number_of_chords'] = '' #info not in this object
    trackObject['chord_difficulty'] = '' #info not in this object
    trackObject['list_of_chords'] = '' #info not in this object
    trackObject['harmonic_variation'] = '' #info not in this object
    trackObject['melodic_variation'] = '' #info not in this object

    playlist_tracks.append(trackObject)
    playlist_track_ids.append(trackObject['track_id'])

audio_features_from_api = spotify.audio_features(playlist_track_ids)

for track, feature in zip(playlist_tracks, audio_features_from_api):
    if track['track_id'] == feature['id']:
        track['key'] = feature['key']
        track['mode'] = feature['mode']
        track['time_signature'] = feature['time_signature']
        track['tempo'] = feature['tempo']
        track['instrumentalness'] = feature['instrumentalness']
        track['speechiness'] = feature['speechiness']
        track['acousticness'] = feature['acousticness']
        track['energy'] = feature['energy']
        track['danceability'] = feature['danceability']
        track['valence'] = feature['valence']


# print(json.dumps(audio_features_from_api, sort_keys=True, indent=4))

client = MongoClient("mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false")
track_collection = client['perceptool-v0']['tracks']

#remove da lista músicas que já estão na base de dados
new_tracks = []
for track in playlist_tracks:
    if track_collection.find_one({"track_id":track['track_id']}) == None:
        new_tracks.append(track)
    else:
        print(f"Documento já existe na base: {track['name']} (id: {track['track_id']})")

if len(new_tracks) > 0:
    track_collection.insert_many(new_tracks)
    print(f"inseridas {len(new_tracks)} novas músicas")
else:
    print("Sem novas músicas")