import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# credenciales
load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-top-read"
))

# PARA ENCONTRAR LAS CANCIONES
def obtener_canciones_top(limit=10, time_range="medium_term"):
    top_tracks = sp.current_user_top_tracks(limit=limit, time_range=time_range)
    canciones = []

    for item in top_tracks['items']:
        nombre = item['name']
        artista = item['artists'][0]['name']
        url = item['external_urls']['spotify']
        canciones.append((nombre, artista, url))

    return canciones


if __name__ == "__main__":
    canciones = obtener_canciones_top()
    for i, (nombre, artista, url) in enumerate(canciones, 1):
        print(f"{i}. {nombre} - {artista}")
        print(f"   {url}")

#GARE USTEDES