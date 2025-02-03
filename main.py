import os
import re
import json
import fcntl
import yt_dlp
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from utils import sanitize_filename, load_config, save_config
import logging
import shutil

# Configuration and state file paths
CONFIG_PATH = "config.yaml"
STATE_FILE = "local.state"
LOCK_FILE = "script.lock"

console = Console()

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"last_checked": {}}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


# Video management

def get_video_list(channel, last_checked, verbose, max_videos_per_channel, max_video_length, max_video_age_months):
    ydl_opts = {
        "quiet": not verbose, 
        "skip_download": True, 
        "extract_flat": "in_playlist", 
        "playlistend": max_videos_per_channel * 2,  # Double the requested videos
        "playlist_items": f"1-{max_videos_per_channel * 2}"  # Ensure we get the first N*2 videos
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel, download=False)
    
    videos = []
    for entry in info.get("entries", []):
        upload_date_str = entry.get("upload_date")
        upload_date = datetime.strptime(upload_date_str, "%Y%m%d") if upload_date_str else None
        
        # Check if the title contains "Trailer" (case insensitive)
        if "trailer" not in entry["title"].lower():
            continue
                
        # Check if the video is within the allowed age
        if max_video_age_months is not None and upload_date:
            max_age_date = datetime.now() - timedelta(days=30 * max_video_age_months)
            if upload_date < max_age_date:
                logging.info(f"Skipping video '{entry['title']}' due to age: uploaded on {upload_date.strftime('%Y-%m-%d')}")
                continue
        
        if last_checked and upload_date and upload_date <= last_checked:
            continue
        
        videos.append({
            "id": entry["id"],
            "title": entry["title"],
            "channel": info["channel"],
            "upload_date": upload_date
        })
    
    return videos

def download_videos(videos, max_res, output_folder, flatten_output_folder):
    for video in videos:
        # Determine the output path based on the flatten_output_folder setting
        if flatten_output_folder:
            output_template = f"{output_folder}/{sanitize_filename(video['title'])}_PG_%(age_limit)05d_upload_%(upload_date)s_dur_%(duration)s_{max_res}p.%(ext)s"
        else:
            # Sanitize channel name for folder creation
            channel_name = sanitize_filename(video.get("channel", "Unknown Channel"))
            channel_folder = output_folder / channel_name
            channel_folder.mkdir(parents=True, exist_ok=True)
            # include youtube downloader duration placeholder in the template so I can parse it
            output_template = f"{channel_folder}/{sanitize_filename(video['title'])}_PG_%(age_limit)05d_upload_%(upload_date)s_dur_%(duration)s_{max_res}p.%(ext)s"

        # Check if the video already exists
        existing_files = list(output_folder.glob(f"{sanitize_filename(video['title'])}_*"))
        if existing_files:
            logging.warning(f"Skipping download, file already exists: {existing_files[0].name}")
            continue
        
        # Download video and dynamically handle extensions
        ydl_opts = {
            "format": f"bestvideo[height<={max_res}]+bestaudio/best[height<={max_res}]",
            "outtmpl": output_template,
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([f"https://www.youtube.com/watch?v={video['id']}"])
            
            if result == 0:  # Check success
                # Locate the downloaded file
                downloaded_file = list(output_folder.glob(f"{sanitize_filename(video['title'])}_*"))
                if downloaded_file:
                    file_path = downloaded_file[0]
                    file_size = file_path.stat().st_size / (1024 ** 2)  # Convert to MB
                    logging.info(f"Downloaded: {video['title']} ({file_size:.2f} MB) as {file_path.suffix} in {max_res}p")
                else:
                    logging.warning(f"Downloaded file not found for: {video['title']}")

def check_disk_space(output_folder, max_gb, verbose):
    # Calculate total size including subdirectories
    total_size = sum(f.stat().st_size for f in Path(output_folder).rglob('*') if f.is_file()) / (1024 ** 3)
    logging.info(f"Total size: {total_size:.2f} GB")
    
    # Delete files until the total size is within the limit
    while total_size > max_gb:
        # Find the oldest file across all subdirectories
        oldest_file = min(Path(output_folder).rglob('*'), key=lambda f: f.stat().st_mtime)
        if verbose:
            console.log(f"Deleting to free space: {oldest_file.name}")
        oldest_file.unlink()
        
        # Recalculate total size
        total_size = sum(f.stat().st_size for f in Path(output_folder).rglob('*') if f.is_file()) / (1024 ** 3)
  # Delete directories that contain no .mp4 or .webm files
    for dir_path in sorted(Path(output_folder).rglob('*'), key=lambda p: -p.parts.count('/')):
        if dir_path.is_dir():
            # Check if directory contains any .mp4 or .webm files
            contains_videos = any(dir_path.glob('*.mp4')) or any(dir_path.glob('*.webm'))
            if not contains_videos:
                if verbose:
                    console.log(f"Deleting empty directory: {dir_path}")
                shutil.rmtree(dir_path)

# Lock management
def acquire_lock():
    lock_file = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_file
    except BlockingIOError:
        console.log("Another instance is already running. Exiting.")
        exit(0)

def release_lock(lock_file):
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close()


def post_download_cleanup(output_folder, max_video_length, max_video_age_months, verbose):
    # Define a regex pattern to extract upload date and duration from filenames
    # this should match the output_template from the download_videos function
    pattern = re.compile(r"_upload_(\d{8})_dur_(\d+)_")

    # Calculate the cutoff date for video age
    max_age_date = datetime.now() - timedelta(days=30 * max_video_age_months)

    for file in Path(output_folder).iterdir():
        if file.is_file():
            match = pattern.search(file.name)
            if match:
                upload_date_str, duration_str = match.groups()
                upload_date = datetime.strptime(upload_date_str, "%Y%m%d")
                duration = int(duration_str)

                # Check if the video is older than the allowed age
                if upload_date < max_age_date:
                    if verbose:
                        console.log(f"Deleting old video: {file.name} (uploaded on {upload_date.strftime('%Y-%m-%d')})")
                    file.unlink()
                    continue

                # Check if the video is longer than the allowed duration
                if duration > max_video_length:
                    if verbose:
                        console.log(f"Deleting long video: {file.name} (duration {duration}s)")
                    file.unlink()

# Main logic

def main():
    config = load_config(CONFIG_PATH)
    state = load_state()
    verbose = config.get("verbose", False)
    output_folder = Path(config["output_folder"])
    output_folder.mkdir(parents=True, exist_ok=True)

    now = datetime.now()

    max_video_length = config.get("max_video_length_seconds", 180)  # Default to 180 seconds
    max_video_age_months = config.get("max_video_age_months", None)

    for channel in config["channels"]:
        logging.info(f"Checking channel: {channel}")

        last_checked = state["last_checked"].get(channel, None)
        if last_checked:
            last_checked = datetime.fromisoformat(last_checked)

        videos = get_video_list(channel, last_checked, verbose, config.get("max_videos_per_channel", 10), max_video_length, max_video_age_months)
        logging.info(f"Found {len(videos)} new videos on channel: {channel}")
        #logging.info(f"Videos: {json.dumps(videos, indent=4)}")
        # exit()


        download_videos(videos[: config["max_videos_per_channel"]], config["max_resolution"], output_folder, config.get("flatten_output_folder", False))

        state["last_checked"][channel] = now.isoformat()

    save_state(state)
    # Perform post-download cleanup
    post_download_cleanup(output_folder, max_video_length, max_video_age_months, verbose)

    check_disk_space(output_folder, config["max_storage_gb"], verbose)

if __name__ == "__main__":
    lock_file = acquire_lock()
    try:
        main()
    finally:
        release_lock(lock_file)
