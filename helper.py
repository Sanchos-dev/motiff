import config
import time
import asyncio
import os
import pwd
import json
from pathlib import Path
import base64
from io import BytesIO
from pathlib import Path
import mutagen
from mutagen.flac import Picture
from PIL import Image



def save_config(inst, val):
    setattr(config, inst, val)
    with open("config.py", "w", encoding="utf-8") as f:
        for k, v in vars(config).items():
            if not k.startswith("__"):
                f.write(f"{k} = {repr(v)}\n")


async def scan_tracks(path):
    tracks = []
    for root, _, files in os.walk(path):
        if hasattr(config, "motiff_music_path") and config.motiff_music_path in root:
            continue
        for file in files:
            filetype = Path(file).suffix.lower()
            if filetype in config.music_formats:
                tracks.append(os.path.join(root, file))
    return tracks


async def scan_playlists(path):
    playlist = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file():
                filename = entry.name
                filetype = Path(filename).suffix.lower()
                if filetype in (".m3u", ".m3u8"):
                    playlist.append(f"{path}/{filename}")
    return playlist


async def scan_for_dirs(path):
    dirs = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                dirs.append(entry.name)
    return dirs


async def parse_track_metadata(track_path):
    title = Path(track_path).stem
    duration = None
    if mutagen:
        try:
            audio = mutagen.File(track_path)
            if audio is not None:
                if hasattr(audio, "info") and hasattr(audio.info, "length"):
                    duration = int(audio.info.length)
                if audio.tags:
                    tag_title = audio.tags.get("TIT2") or audio.tags.get("title")
                    if tag_title:
                        title = str(tag_title[0] if isinstance(tag_title, list) else tag_title)
        except Exception:
            pass

    return {
        "path": str(track_path),
        "title": title,
        "duration": duration
    }

async def parse_cover(track_path, output_dir=None):
    path_obj = Path(track_path)
    if output_dir:
        output_path = Path(output_dir) / f"{path_obj.stem}.png"
    else:
        output_path = path_obj.with_suffix(".png")

    image_data = None

    try:
        audio = mutagen.File(track_path)
        if audio is None:
            return None

        if hasattr(audio, "pictures") and audio.pictures:
            image_data = audio.pictures[0].data

        elif audio.tags:
            if "covr" in audio.tags and audio.tags["covr"]:
                image_data = bytes(audio.tags["covr"][0])
            elif "metadata_block_picture" in audio.tags:
                b64 = audio.tags["metadata_block_picture"][0]
                pic = Picture(base64.b64decode(b64))
                image_data = pic.data
            else:
                for tag in audio.tags.values():
                    if getattr(tag, "FrameID", None) == "APIC" or tag.__class__.__name__ == "APIC":
                        image_data = tag.data
                        break

        if image_data:
            if Image:
                img = Image.open(BytesIO(image_data))
                img.save(output_path, format="PNG")
            else:
                with open(output_path, "wb") as f:
                    f.write(image_data)
            return str(output_path)
    except Exception:
        pass
    return None

async def parse_m3u(file_path):
    tracklist = []
    path_obj = Path(file_path)
    if not path_obj.is_file():
        return tracklist

    playlist_dir = path_obj.parent

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

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

            track_info = await parse_track_metadata(str(track_path))
            if current_metadata.get("title"):
                track_info["title"] = current_metadata["title"]
            if current_metadata.get("duration"):
                track_info["duration"] = current_metadata["duration"]

            tracklist.append(track_info)
            current_metadata = {}

    return tracklist


async def update_unsorted_playlist():
    tr = await scan_tracks(config.music_path)
    with open(f"{config.motiff_music_path}/Playlists/Unsorted/Unsorted.m3u", "w", encoding="utf-8") as file:
        for i in tr:
            await parse_cover(i, output_dir=f"{config.motiff_music_path}/chache/")
            file.write(f"{i}\n")
    return True


async def fast_update():
    pass



async def get_tracklist(playlist_name):
    with open("database.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    playlists = data.get("playlists", {})
    playlist = playlists.get(playlist_name)
    if not playlist:
        return []
    track_titles = [track["title"] for track in playlist.get("tracks", [])]
    return track_titles



async def update_database():
    await update_unsorted_playlist()

    playlists_dir = Path(config.motiff_music_path) / "Playlists"
    playlists_data = {}

    if playlists_dir.exists():
        for entry in os.scandir(playlists_dir):
            if entry.is_dir():
                p_dir = Path(entry.path)
                p_name = entry.name
                m3u_files = list(p_dir.glob("*.m3u")) + list(p_dir.glob("*.m3u8"))

                if m3u_files:
                    target_m3u = m3u_files[0]
                else:
                    target_m3u = p_dir / f"{p_name}.m3u"
                    tracks_in_dir = []
                    for root, _, files in os.walk(p_dir):
                        for file in files:
                            if Path(file).suffix.lower() in config.music_formats:
                                tracks_in_dir.append(os.path.join(root, file))
                    with open(target_m3u, "w", encoding="utf-8") as f:
                        for tr in tracks_in_dir:
                            f.write(f"{tr}\n")

                parsed = await parse_m3u(str(target_m3u))
                playlists_data[p_name] = {
                    "file_path": str(target_m3u),
                    "tracks": parsed
                }

    all_tracks = await scan_tracks(config.music_path)

    db_content = {
        "updated_at": time.time(),
        "total_tracks": len(all_tracks),
        "tracks": all_tracks,
        "playlists": playlists_data
    }

    with open("database.json", "w", encoding="utf-8") as f:
        json.dump(db_content, f, ensure_ascii=False, indent=4)

    return True


async def startup():
    username = pwd.getpwuid(os.getuid()).pw_name
    save_config("music_path", f"/home/{username}/Music")
    with open("database.json", "w+") as f:
        f.write("")
    save_config("motiff_music_path", f"/home/{username}/Music/Motiff")
    os.makedirs(config.motiff_music_path, exist_ok=True)
    os.makedirs(f"{config.motiff_music_path}/Playlists", exist_ok=True)
    os.makedirs(f"{config.motiff_music_path}/Playlists/Favourites", exist_ok=True)
    with open(f"{config.motiff_music_path}/Playlists/Favourites/Favourites.m3u", "w+") as f:
        f.write("")
    os.makedirs(f"{config.motiff_music_path}/Playlists/Unsorted", exist_ok=True)
    with open(f"{config.motiff_music_path}/Playlists/Unsorted/Unsorted.m3u", "w+") as f:
        f.write("")
    os.makedirs(f"{config.motiff_music_path}/chache", exist_ok=True)
    await update_database()
    

    return True