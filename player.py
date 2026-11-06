import vlc


class Player:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.is_playing = False
        self.current_path = None

    async def play(self, path: str, start_time: int = 0):
        self.current_path = path
        media = self.instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        self.is_playing = True
        
        if start_time > 0:
            self.player.set_time(int(start_time * 1000))

    async def toggle_pause(self):
        if self.current_path is None:
            return False

        if self.player.get_state() == vlc.State.Ended:
            self.player.stop()
            self.player.play()
            self.is_playing = True
            return True

        self.player.pause()
        self.is_playing = not self.is_playing
        return self.is_playing

    async def stop(self):
        self.player.stop()
        self.is_playing = False

    async def set_time(self, seconds: float):
        if self.current_path:
            self.player.set_time(int(seconds * 1000))

    def get_time(self) -> float:
        t = self.player.get_time()
        return t / 1000.0 if t != -1 else 0.0

    def is_ended(self) -> bool:
        return self.player.get_state() == vlc.State.Ended