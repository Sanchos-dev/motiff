import helper
import asyncio
import flet as ft
import config
from player import Player

class UI:
    def __init__(self):
        self.player = Player()
        self.player_task: asyncio.Task | None = None

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
        #helper.save_config("first_time", False)

        page.clean()
        await self.main(page)



    async def main(self, page: ft.Page):
        page.title = "Motiff"






        track_lil_cover = ft.Image(
            src="https://picsum.photos/200/200",
            width=50,
            height=50,
            fit=ft.BoxFit.COVER,
            border_radius=5,
        )

        track_block = ft.Container(
            margin=10,
            padding=12,

            border_radius=15,
            content=ft.Row(
                spacing=4,
                controls=[
                    track_lil_cover,
               	    ft.Text("Track_name", size=12, weight=ft.FontWeight.W_500),
                    time_row,
                    controls_row,
                    ],
                ),
            ),



        track_cover = ft.Image(
            src="https://picsum.photos/200/200",
            width=200,
            height=200,
            fit=ft.BoxFit.COVER,
            border_radius=12,
        )
        track_name_text = ft.Text("Track Title", size=22, weight=ft.FontWeight.BOLD)
        artist_text = ft.Text(
            "Artist Name", size=16, weight=ft.FontWeight.W_400, opacity=0.8
        )


        progress_slider = ft.Slider(
            min=0,
            max=225, 
            value=45, 
        )

        time_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("0:45", size=12, weight=ft.FontWeight.W_500),
                ft.Text("3:45", size=12, weight=ft.FontWeight.W_500),
            ],
        )

        controls_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(icon=ft.Icons.SHUFFLE),
                ft.IconButton(
                    icon=ft.Icons.SKIP_PREVIOUS, icon_size=28
                ),
                ft.IconButton(
                    icon=ft.Icons.PLAY_CIRCLE_FILL,
                    icon_size=46,

                ),
                ft.IconButton(
                    icon=ft.Icons.SKIP_NEXT, icon_size=28
                ),
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
                    content=ft.Text(
                        "Now Playing", size=20, weight=ft.FontWeight.W_600
                    ),
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

        layout = ft.Row(
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Container(
                    expand=True,
                    margin=10,
                    bgcolor=ft.Colors.AMBER,
                    border_radius=10,
                    content=ft.Text("WIP"),
                ),
                ft.Container(
                    expand=True,
                    content=right_panel_contents,
                ),
            ],
        )

        page.add(layout)
        page.update()