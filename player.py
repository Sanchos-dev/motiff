import asyncio
import vlc


class Player:
    def __init__(self):
        self.is_playing = False

    async def play(self, title, start_time):
        self.is_playing = True
        
    async def stop(self):
        self.is_playing = False