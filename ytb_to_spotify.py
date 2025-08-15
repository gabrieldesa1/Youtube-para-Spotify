import os
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Credenciais do Spotify 
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# URL da playlist do YouTube
YOUTUBE_PLAYLIST_ID = "PLn2rD8fIUgA1wwmPqYEm097dBz3b_4WSA"
SPOTIFY_PLAYLIST_NAME = "Ainda bem que eu sou Flamengo"

# Autenticação no Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-modify-public"
))

# Autenticação no YouTube
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
credentials = flow.run_local_server(port=0)
youtube = build("youtube", "v3", credentials=credentials)


def get_youtube_playlist_items(playlist_id):
    songs = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response["items"]:
            title = item["snippet"]["title"]
            # Limpa títulos que contenham coisas como (Vídeo oficial), [Ao Vivo], etc.
            clean_title = re.sub(r"[\(\[].*?[\)\]]", "", title).strip()
            songs.append(clean_title)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return songs

# Buscar música no Spotify
def search_spotify_track(track_name):
    results = sp.search(q=track_name, type="track", limit=1)
    tracks = results.get("tracks", {}).get("items", [])

    if tracks: 
        return tracks[0]["id"]
    return None

# Criar playlist no Spotify
def create_spotify_playlist(name, track_ids):
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=name)

    if track_ids:
        sp.playlist_add_items(playlist_id=playlist["id"], items=track_ids)
        return playlist["external_urls"]["spotify"]
    
# Main
print("Lendo playlist do Youtube...")
songs = get_youtube_playlist_items(YOUTUBE_PLAYLIST_ID)
print(f"Encontradas {len(songs)} músicas.")

track_ids = []

for song in songs:
    print(f"Buscando: {song}")
    track_id = search_spotify_track(song)

    if track_id:
        track_ids.append(track_id)
    else:
        print(f"Não encontrada no Spotify: {song}")

print("Criando playlist no Spotify...")
playlist_url = create_spotify_playlist(SPOTIFY_PLAYLIST_NAME, track_ids)
print(f"Playlist criada com sucesso: {playlist_url}")
