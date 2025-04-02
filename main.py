import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import flet as ft

# credenciales
load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-top-read"
))

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

#Flet
def main(page: ft.Page):
    page.title = "Recophy"
    page.scroll = ft.ScrollMode.AUTO

    lista_canciones = ft.Column()
    lista_recomendaciones = ft.Column()

    def cargar_canciones():
        lista_canciones.controls.clear()
        canciones = obtener_canciones_top()

        for nombre, artista, url in canciones:
            boton = ft.ElevatedButton(
                text=f"{nombre} - {artista}",
                on_click=lambda e, nombre=nombre: mostrar_recomendaciones(nombre)
            )
            lista_canciones.controls.append(boton)

        page.update()

    def mostrar_recomendaciones(nombre_cancion):
        lista_recomendaciones.controls.clear()

        
        resultados = sp.search(q=nombre_cancion, type='track', limit=1)
        if resultados['tracks']['items']:
            track_id = resultados['tracks']['items'][0]['id']

            
            recomendaciones = sp.recommendations(seed_tracks=[track_id], limit=5)

            for track in recomendaciones['tracks']:
                nombre = track['name']
                artista = track['artists'][0]['name']
                url = track['external_urls']['spotify']

                lista_recomendaciones.controls.append(
                    ft.Text(f"{nombre} - {artista}"),
                )
                lista_recomendaciones.controls.append(
                    ft.TextButton(text="🔗 Abrir en Spotify", url=url)
                )
        else:
            lista_recomendaciones.controls.append(ft.Text("No se encontraron recomendaciones."))

        page.update()

    page.add(
        ft.Text("Tus canciones más escuchadas:", size=20, weight="bold"),
        ft.ElevatedButton("Cargar canciones", on_click=lambda _: cargar_canciones()),
        lista_canciones,
        ft.Divider(),
        ft.Text("Recomendaciones:", size=20, weight="bold"),
        lista_recomendaciones,
    )

ft.app(target=main)