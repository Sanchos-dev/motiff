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
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.START
        
        page.add(ft.Text("Welcome to Motiff", size=24))
        page.update()