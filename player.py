import asyncio

class Player:
    def __init__(self):
        self.is_playing = False

    async def play(self, track_name):
        self.is_playing = True
        
    async def stop(self):
        self.is_playing = False