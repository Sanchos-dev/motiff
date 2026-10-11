import config
import time
import asyncio
import os
import pwd
from pathlib import Path

def save_config(inst, val):
    setattr(config, inst, val)
    with open("config.py", "w", encoding="utf-8") as f:
        for k, v in vars(config).items():
            if not k.startswith("__"):
                f.write(f"{k} = {repr(v)}\n")
async def scan_tracks(path):
	tracks = []
	with os.scandir(path) as entries:
		for entry in entries:
			if entry.is_file():
				filename = entry.name
				filetype = Path(filename).suffix
				if filetype in config.music_formats:
					print(f"mus: A_path: {path}/{filename}")
					tracks.append(f"{path}/{filename}")
			elif entry.is_dir():
				pass
	return tracks

async def scan_playlists(path):
	playlist = []
	with os.scandir(path) as entries:
		for entry in entries:
			if entry.is_file():
				filename = entry.name
				filetype = Path(filename).suffix
				if filetype in (".m3u", ".m3u8"):
					playlist.append(f"{path}/{filename}")
			elif entry.is_dir():
				pass
	return playlist

async def scan_for_dirs(path):
	dirs = []
	with os.scandir(path) as entries:
		for entry in entries:
			if entry.is_file():
				pass
			elif entry.is_dir():
				dir_name = entry.name
				dirs.append(dir_name)
				pass
	return dirs

async def parse_m3u(file_path):
    tracklist = []
    path_obj = Path(file_path)
    if not path_obj.is_file():
        return tracklist
    playlist_dir = path_obj.parent
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return tracklist
    current_metadata = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF:"):
            info = line[8:]
            parts = info.split(",", 1)
            duration = None
            title = None
            if len(parts) >= 1:
                try:
                    duration = int(float(parts[0].strip()))
                except ValueError:
                    duration = None
            if len(parts) == 2:
                title = parts[1].strip()
            current_metadata = {
                "duration": duration,
                "title": title
            }
        elif line.startswith("#"):
            continue
        else:
            track_path = Path(line)
            if not track_path.is_absolute():
                track_path = (playlist_dir / track_path).resolve()
            track_entry = {
                "path": str(track_path),
                "title": current_metadata.get("title") or track_path.stem,
                "duration": current_metadata.get("duration")
            }
            tracklist.append(track_entry)
            current_metadata = {}
    return tracklist

async def update_unsorted_playlist():
	tr = await scan_tracks(config.music_path)
	with open(f"{config.motiff_music_path}/Playlists/Unsorted/Unsorted.m3u", "w", encoding="utf-8") as file:
		for i in tr:
			file.write(f"{i}\n")
	return True

async def update_database():
	await update_unsorted_playlist()
	pass

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
	os.makedirs(f"{config.motiff_music_path}/Playlists/Unsorted", exist_ok=True)
	with open(f"{config.motiff_music_path}/Playlists/Unsorted/Unsorted.m3u", "w+") as f:
		f.write("")
		f.close()
	await update_unsorted_playlist()
	
	return True
