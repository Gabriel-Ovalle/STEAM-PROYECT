import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import flet as ft

# Load environment variables
load_dotenv("e.env")

# Spotify authentication
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-top-read user-read-private"
    ))
except Exception as e:
    print(f"Error initializing Spotify: {e}")
    exit()

def obtener_canciones_top(limit=5, time_range="medium_term"):
    try:
        top_tracks = sp.current_user_top_tracks(limit=limit, time_range=time_range)
        return [
            (
                track['name'],
                track['artists'][0]['name'],
                track['id']
            ) for track in top_tracks['items']
        ]
    except Exception as e:
        print(f"Error getting top tracks: {e}")
        return []

def main(page: ft.Page):
    page.title = "Recophy"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    lista_canciones = ft.Column()
    lista_recomendaciones = ft.Column()

    # Error alert
    def show_error(message):
        page.snack_bar = ft.SnackBar(ft.Text(f"Error: {message}"), bgcolor=ft.colors.RED)
        page.snack_bar.open = True
        page.update()

    # Load top tracks
    def cargar_canciones(e=None):
        try:
            canciones = obtener_canciones_top()
            if not canciones:
                show_error("No se encontraron canciones")
                return

            lista_canciones.controls.clear()
            seed_tracks = [track[2] for track in canciones]
            page.session.set("seed_tracks", seed_tracks[:5])

            for nombre, artista, track_id in canciones:
                lista_canciones.controls.append(
                    ft.ElevatedButton(
                        text=f"{nombre} - {artista}",
                        on_click=lambda e, tid=track_id: mostrar_recomendaciones(tid)
                    )
                )
            page.update()
        except Exception as e:
            show_error(str(e))

    # Show recommendations for single track
    def mostrar_recomendaciones(track_id):
        try:
            recomendaciones = sp.recommendations(seed_tracks=[track_id], limit=5)
            mostrar_resultados(recomendaciones)
        except Exception as e:
            show_error(str(e))

    # Show recommendations from all top tracks
    def generar_recomendaciones(e):
        try:
            seed_tracks = page.session.get("seed_tracks")
            if not seed_tracks:
                show_error("Carga tus canciones primero")
                return

            recomendaciones = sp.recommendations(seed_tracks=seed_tracks, limit=10)
            mostrar_resultados(recomendaciones)
        except Exception as e:
            show_error(str(e))

    # Helper to display recommendations
    def mostrar_resultados(recomendaciones):
        lista_recomendaciones.controls.clear()
        if not recomendaciones.get('tracks'):
            lista_recomendaciones.controls.append(ft.Text("No hay recomendaciones"))
            page.update()
            return

        for track in recomendaciones['tracks']:
            nombre = track['name']
            artista = track['artists'][0]['name']
            url = track['external_urls']['spotify']
            imagen_url = track['album']['images'][1]['url'] if track['album']['images'] else ""

            lista_recomendaciones.controls.append(
                ft.Row([
                    ft.Image(src=imagen_url, width=60, height=60),
                    ft.Column([
                        ft.Text(f"{nombre} - {artista}"),
                        ft.TextButton("🔗 Spotify", url=url),
                    ])
                ])
            )
        page.update()

    # User profile
    def abrir_perfil_usuario(e=None):
        try:
            user = sp.current_user()
            page.dialog = ft.AlertDialog(
                title=ft.Text(f"Hola, {user.get('display_name', 'Usuario')}!"),
                content=ft.TextButton("Ver perfil", url=user["external_urls"]["spotify"]),
                open=True
            )
            page.update()
        except Exception as e:
            show_error(str(e))

    # UI Setup
    page.add(
        ft.Text("Tus canciones más escuchadas:", size=20, weight="bold"),
        ft.Row([
            ft.ElevatedButton("Cargar canciones", on_click=cargar_canciones),
            ft.ElevatedButton("Ver perfil", on_click=abrir_perfil_usuario),
            ft.ElevatedButton("🎵 Recomendaciones", on_click=generar_recomendaciones),
        ]),
        lista_canciones,
        ft.Divider(),
        ft.Text("Recomendaciones:", size=20, weight="bold"),
        lista_recomendaciones,
    )

    # Initial load
    page.update()

ft.app(target=main)