import config
import time
import asyncio
import os
import pwd


def save_config(inst, val):
    setattr(config, inst, val)
    with open("config.py", "w", encoding="utf-8") as f:
        for k, v in vars(config).items():
            if not k.startswith("__"):
                f.write(f"{k} = {repr(v)}\n")
async def startup():
	username = pwd.getpwuid(os.getuid()).pw_name
	save_config("music_path",f"/home/{username}/Music")
	with open("database.json", "w+") as f:
		f.write("")
		f.close()
	save_config("motiff_music_path",f"/home/{username}/Music/Motiff")

	os.makedirs(config.motiff_music_path, exist_ok=True)
	os.makedirs(f"{config.motiff_music_path}/Playlists", exist_ok=True)
	os.makedirs(f"{config.motiff_music_path}/Playlists/Favourites", exist_ok=True)
	with open(f"{config.motiff_music_path}/Playlists/Favourites/Favourites.m3u", "w+") as f:
		f.write("")
		f.close()
	os.makedirs(f"{config.motiff_music_path}/Unsorted", exist_ok=True)
	

	return True
