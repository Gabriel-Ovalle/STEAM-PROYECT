import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import flet as ft


=======
# credenciales
load_dotenv("e.env")
>>>>>>> 7d1f997fb66a2d897fe977ea3bef36f5bdfa0b8c


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-top-read user-read-private"
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

# Flet
def main(page: ft.Page):
    page.title = "Recophy"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    lista_canciones = ft.Column()
    lista_recomendaciones = ft.Column()

    def cargar_canciones(e=None):
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
                imagen_url = track['album']['images'][1]['url'] if track['album']['images'] else ""

                fila = ft.Row([
                    ft.Image(src=imagen_url, width=60, height=60),
                    ft.Column([
                        ft.Text(f"{nombre} - {artista}"),
                        ft.TextButton(text="🔗 Spotify", url=url),
                    ])
                ])
                lista_recomendaciones.controls.append(fila)
        else:
            lista_recomendaciones.controls.append(ft.Text("No se encontraron recomendaciones."))

        page.update()

    def abrir_perfil_usuario(e=None):
        user = sp.current_user()
        nombre = user.get("display_name", "Usuario")
        url = user["external_urls"]["spotify"]
        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Hola, {nombre}!"),
            content=ft.TextButton(text="🔗 Ver tu perfil de Spotify", url=url),
            open=True,
        )
        page.update()

    
    page.add(
        ft.Text("Tus canciones más escuchadas:", size=20, weight="bold"),
        ft.Row([
            ft.ElevatedButton("Cargar canciones", on_click=cargar_canciones),
            ft.ElevatedButton("Ver perfil", on_click=abrir_perfil_usuario),
        ]),
        lista_canciones,
        ft.Divider(),
        ft.Text("Recomendaciones:", size=20, weight="bold"),
        lista_recomendaciones,
    )
     def abrir_perfil_usuario():
    user = sp.current_user()
    nombre = user.get("display_name", "Usuario")
    url = user["external_urls"]["spotify"]
    page.dialog = ft.AlertDialog(
        title=ft.Text(f"Hola, {nombre}!"),
        content=ft.TextButton(text=" Ver tu perfil de Spotify", url=url),
        open=True,
    )
    page.update()
    ft.ElevatedButton("Ver perfil", on_click=lambda _: abrir_perfil_usuario()),

ft.app(target=main)

#ayisyen?
