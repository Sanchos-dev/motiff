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

        lil_text = ft.Text("Preparing...", size=14, weight=ft.FontWeight.W_600)
        name_text = ft.Text("Motiff Startup", size=24, weight=ft.FontWeight.W_600)
        progress = ft.ProgressBar(width=400, color=ft.Colors.AMBER)

        page.add(name_text, lil_text, progress)
        page.update()

        if await helper.startup():
            page.clean()
            await self.main(page)

    async def main(self, page: ft.Page):
        page.title = "Motiff"
        right_panel_contents = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                    ft.Container(
                    	expand=True,
                        margin=10,
                        padding=10,
                        bgcolor=ft.Colors.AMBER,
                        border_radius=10,
                        content=ft.Text("Non clickable"),
                    ),
                    ft.Container(
                    	expand=True,
                        margin=10,
                        padding=10,
                        bgcolor=ft.Colors.AMBER,
                        border_radius=10,
                        content=ft.Text("Non clickable"),
                    ),
                    ft.Container(
                    	expand=True,
                        margin=10,
                        padding=10,
                        bgcolor=ft.Colors.AMBER,
                        border_radius=10,
                        content=ft.Text("Non clickable"),
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
                        padding=10,
                        bgcolor=ft.Colors.AMBER,
                        border_radius=10,
                        content=ft.Text("Non clickable"),
                    ),
                    ft.Container(
                    	expand=True,
                        margin=10,
                        padding=10,
                        bgcolor=ft.Colors.BLUE,
                        border_radius=10,
                        content=right_panel_contents,
                    ),
            ],
         )
        page.add(layout)
        page.update()