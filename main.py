import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import flet as ft
import webbrowser

#last software development project ever. feels like yesterday i was in 11th grade cogiendo python con usted, lui, y hector, it also feels like yesterday cuando le di su pela en brawlhalla.
#-Fitch
#P.S.: me gradue invicto
load_dotenv("e.env")


sp = None

def main(page: ft.Page):
    page.title = "Recophy"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    lista_elementos = ft.Column()
    lista_recomendaciones = ft.Column()


    auth_text = ft.Text("Not authenticated", color=ft.colors.RED)
    
    def show_error(message):
        page.snack_bar = ft.SnackBar(
            ft.Text(message, color=ft.colors.WHITE),
            bgcolor=ft.colors.RED_800,
            duration=3000
        )
        page.snack_bar.open = True
        page.update()

    def link_account(e):
        global sp
        try:
            auth_manager = SpotifyOAuth(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
                scope="user-top-read user-read-private",
                show_dialog=True
            )
            
            auth_url = auth_manager.get_authorize_url()
            webbrowser.open(auth_url) 
            
            token_info = auth_manager.get_access_token()
            if token_info:
                sp = spotipy.Spotify(auth_manager=auth_manager)
                auth_text.value = "Authenticated!"
                auth_text.color = ft.colors.GREEN
                page.update()
        except Exception as e:
            show_error(f"Auth error: {str(e)}")

    def check_authentication():
        return sp and sp.auth_manager.get_cached_token()

    def get_top_tracks(limit=5):
        if not check_authentication():
            show_error("Authenticate first")
            return []
        try:
            results = sp.current_user_top_tracks(limit=limit)
            return [(item['name'], item['artists'][0]['name'], item['id']) for item in results['items']]
        except Exception as e:
            show_error(f"Track error: {str(e)}")
            return []

    def get_top_artists(limit=5):
        if not check_authentication():
            show_error("Authenticate first")
            return []
        try:
            results = sp.current_user_top_artists(limit=limit)
            return [(item['name'], item['id']) for item in results['items']]
        except Exception as e:
            show_error(f"Artist error: {str(e)}")
            return []

    def show_recommendations(seed_type, seed_ids):
        if not check_authentication():
            show_error("Authenticate first")
            return
        try:
            recommendations = sp.recommendations(
                **{seed_type: seed_ids},
                limit=10
            )
            display_recommendations(recommendations)
        except Exception as e:
            show_error(f"Recommendation error: {str(e)}")

    def display_recommendations(recommendations):
        lista_recomendaciones.controls.clear()
        if not recommendations.get('tracks'):
            lista_recomendaciones.controls.append(ft.Text("No recommendations found"))
            page.update()
            return

        for track in recommendations['tracks']:
            nombre = track['name']
            artista = track['artists'][0]['name']
            url = track['external_urls']['spotify']
            imagen_url = track['album']['images'][1]['url'] if track['album']['images'] else ""

            lista_recomendaciones.controls.append(
                ft.Row([
                    ft.Image(src=imagen_url, width=60, height=60),
                    ft.Column([
                        ft.Text(f"{nombre} - {artista}"),
                        ft.TextButton("Open in Spotify", url=url),
                    ])
                ])
            )
        page.update()

    def load_tracks(e):
        tracks = get_top_tracks()
        if not tracks:
            return

        page.session.set("seed_type", "seed_tracks")
        page.session.set("seeds", [track[2] for track in tracks][:5])

        lista_elementos.controls.clear()
        for nombre, artista, track_id in tracks:
            lista_elementos.controls.append(
                ft.ElevatedButton(
                    f"🎵 {nombre} - {artista}",
                    on_click=lambda e, tid=track_id: show_recommendations("seed_tracks", [tid])
                )
            )
        page.update()

    def load_artists(e):
        artists = get_top_artists()
        if not artists:
            return

        page.session.set("seed_type", "seed_artists")
        page.session.set("seeds", [artist[1] for artist in artists][:5])

        lista_elementos.controls.clear()
        for nombre, artist_id in artists:
            lista_elementos.controls.append(
                ft.ElevatedButton(
                    f"🎤 {nombre}",
                    on_click=lambda e, aid=artist_id: show_recommendations("seed_artists", [aid])
                )
            )
        page.update()

    def generate_recommendations(e):
        seed_type = page.session.get("seed_type")
        seeds = page.session.get("seeds", [])
        
        if not seeds or not seed_type:
            show_error("Load tracks/artists first")
            return

        show_recommendations(seed_type, seeds)

    page.add(
        ft.Row([
            ft.ElevatedButton("🔗 Link Spotify Account", on_click=link_account),
            auth_text
        ]),
        ft.Divider(),
        ft.Text("Load your data:", size=20, weight="bold"),
        ft.Row([
            ft.ElevatedButton("💿 Load Top Tracks", on_click=load_tracks),
            ft.ElevatedButton("🎤 Load Top Artists", on_click=load_artists),
        ]),
        lista_elementos,
        ft.Divider(),
        ft.Text("Your Recommendations:", size=20, weight="bold"),
        ft.ElevatedButton("✨ Generate Recommendations", on_click=generate_recommendations),
        lista_recomendaciones
    )

    page.update()

ft.app(target=main)