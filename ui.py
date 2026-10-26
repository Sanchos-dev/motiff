### full ui mode

import os
import asyncio
import flet as ft
import config
import helper
from player import Player


def format_time(seconds):
    if not seconds:
        return "0:00"
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"


class UI:
    def __init__(self):
        self.player = Player()

    async def start(self, page: ft.Page):
        if not config.first_time:
            await self.main(page)
            return

        page.title = "Motiff Startup"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        name_text = ft.Text("Motiff Startup", size=24, weight=ft.FontWeight.W_600)
        lil_text = ft.Text("Preparing...", size=14, weight=ft.FontWeight.W_600)
        progress = ft.ProgressBar(width=400, color=ft.Colors.AMBER)

        page.add(name_text, lil_text, progress)
        page.update()
        await asyncio.sleep(0.5)
        await helper.startup()
        helper.save_config("first_time", False)

        page.clean()
        await self.main(page)

    async def main(self, page: ft.Page):
        page.title = "Motiff"

        track_cover = ft.Image(
            src="src/unknown_track.jpg",
            width=200,
            height=200,
            fit=ft.BoxFit.COVER,
            border_radius=12,
        )
        track_name_text = ft.Text("choose track", size=20, weight=ft.FontWeight.BOLD)
        artist_text = ft.Text("—", size=14, opacity=0.8)

        progress_slider = ft.Slider(min=0, max=100, value=0)

        time_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("0:00", size=12),
                ft.Text("0:00", size=12),
            ],
        )

        controls_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(icon=ft.Icons.SHUFFLE),
                ft.IconButton(icon=ft.Icons.SKIP_PREVIOUS, icon_size=28),
                ft.IconButton(icon=ft.Icons.PLAY_CIRCLE_FILL, icon_size=46),
                ft.IconButton(icon=ft.Icons.SKIP_NEXT, icon_size=28),
                ft.IconButton(icon=ft.Icons.REPEAT),
            ],
        )

        right_panel_contents = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(
                    alignment=ft.Alignment.TOP_CENTER,
                    padding=ft.Padding.only(top=10),
                    content=ft.Text("Now Playing", size=20, weight=ft.FontWeight.W_600),
                ),
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            track_cover,
                            track_name_text,
                            artist_text,
                        ],
                    ),
                ),
                ft.Container(
                    margin=10,
                    padding=12,
                    border_radius=15,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        spacing=4,
                        controls=[
                            progress_slider,
                            time_row,
                            controls_row,
                        ],
                    ),
                ),
            ],
        )

        left_column = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=8,
        )

        async def play_track(track, artist, cover):
            title = track.get("title", "")
            duration = track.get("duration", 0)

            track_name_text.value = title
            artist_text.value = artist
            track_cover.src = cover
            progress_slider.max = duration if duration else 100
            progress_slider.value = 0
            time_row.controls[0].value = "0:00"
            time_row.controls[1].value = format_time(duration)

            await self.player.play(title)
            page.update()

        async def show_tracks(playlist_name):
            left_column.controls.clear()

            back_btn = ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: asyncio.create_task(show_playlists()),
            )
            title = ft.Text(playlist_name, size=18, weight=ft.FontWeight.BOLD)
            left_column.controls.append(ft.Row([back_btn, title]))

            tracks = await helper.get_tracklist(playlist_name)

            for track in tracks:
                path = track.get("path", "")
                title = track.get("title", "")
                duration = track.get("duration", 0)

                filename = os.path.basename(path)
                artist = "idk"
                if " - " in filename:
                    artist = filename.split(" - ")[0]

                cover_file = os.path.splitext(filename)[0] + ".png"
                cover_path = os.path.join(config.motiff_music_path, "chache", cover_file)
                if not os.path.exists(cover_path):
                    cover_path = "src/unknown_track.jpg"

                track_card = ft.Container(
                    padding=8,
                    border_radius=8,
                    bgcolor=ft.Colors.BLACK12,
                    ink=True,
                    on_click=lambda e, t=track, a=artist, c=cover_path: asyncio.create_task(play_track(t, a, c)),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                expand=True,
                                controls=[
                                    ft.Image(
                                        src=cover_path,
                                        width=45,
                                        height=45,
                                        fit=ft.BoxFit.COVER,
                                        border_radius=6,
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        expand=True,
                                        controls=[
                                            ft.Text(title, size=14, weight=ft.FontWeight.W_500, max_lines=1),
                                            ft.Text(artist, size=11, opacity=0.7, max_lines=1),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Text(format_time(duration), size=12),
                        ],
                    ),
                )
                left_column.controls.append(track_card)

            page.update()

        async def show_playlists():
            left_column.controls.clear()
            header = ft.Text("Playlists", size=20, weight=ft.FontWeight.BOLD)
            left_column.controls.append(header)

            playlists = await helper.get_playlists()
            for name in playlists:
                card = ft.Container(
                    height=60,
                    padding=10,
                    margin=5,
                    bgcolor=ft.Colors.BLACK12,
                    border_radius=10,
                    ink=True,
                    alignment=ft.Alignment.CENTER_LEFT,
                    on_click=lambda e, p=name: asyncio.create_task(show_tracks(p)),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(name, size=16, weight=ft.FontWeight.W_600),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        ],
                    ),
                )
                left_column.controls.append(card)

            page.update()

        await show_playlists()

        layout = ft.Row(
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Container(
                    expand=True,
                    margin=10,
                    padding=10,
                    border_radius=10,
                    content=left_column,
                ),
                ft.Container(
                    expand=True,
                    content=right_panel_contents,
                ),
            ],
        )

        page.add(layout)
        page.update()