# YouTube Trailer Downloader

This script automates the downloading and management of YouTube videos, specifically trailers, based on specified configurations.

## Features

- **Fetch Videos**: Automatically fetches videos from predefined YouTube channels.
- **Download Management**: Downloads the latest videos based on configuration limits like age, resolution, and the maximum number of videos per channel.
- **Storage Management**: Manages local storage by deleting older or excess files to stay within defined space limits.
- **Verbose Mode**: Configurable logging for detailed updates (enabled via `config.yaml`).
- **Progress Bar**: Uses the `rich` library for clear and user-friendly progress visualization.
- **File Management**: Deletes videos based on age and storage constraints.
- **Locking Mechanism**: Prevents multiple script instances from running simultaneously.
- **State Tracking**: Maintains the last processed date for each channel in `local.state`.

## Recent Updates

1. **Quiet Mode for yt_dlp**: 
   - Implemented a custom `QuietLogger` to suppress all output from `yt_dlp`, ensuring the script runs silently without console output.

2. **Improved Video Deletion Logic**:
   - The script now uses the upload date extracted from the filename to determine the age of the video, preventing premature deletion of freshly downloaded videos.

3. **Post-Download Cleanup**:
   - Added a `post_download_cleanup` function to delete videos based on age and duration constraints, using regex to extract metadata from filenames.

4. **Disk Space Management**:
   - Enhanced the `check_disk_space` function to delete the oldest files until the total size is within the specified limit, and to remove empty directories.

## Configuration

The `config.yaml` file specifies:

- **Channels**: List of YouTube channels to monitor.
- **Max Videos**: Maximum number of videos to download per channel.
- **Resolution**: Maximum resolution for downloaded videos.
- **Storage Size**: Maximum storage size for the trailers directory.
- **Verbose Mode**: Enable or disable detailed logging.

## Usage

1. **Install Dependencies**:
   - Ensure you have Python installed along with the required packages: `yt_dlp`, `rich`, `PyYAML`.

2. **Run the Script**:
   - Execute the script using Python: `python main.py`.

3. **Configuration**:
   - Modify `config.yaml` to set your preferences for channels, video limits, and storage constraints.

## Notes

- Ensure the `config.yaml` and `local.state` files are correctly set up in the script's directory.
- The script uses a locking mechanism to prevent concurrent executions, ensuring safe and consistent operations.

## License

This project is licensed under the MIT License.

---

## Setup

### Prerequisites

1. **Install Python**:
   - Ensure Python 3.10 or higher is installed.
   - Use [pyenv](https://github.com/pyenv/pyenv) to manage Python versions if necessary:
     ```bash
     curl https://pyenv.run | bash
     export PATH="$HOME/.pyenv/bin:$PATH"
     eval "$(pyenv init --path)"
     eval "$(pyenv virtualenv-init -)"
     pyenv install 3.10.9
     pyenv local 3.10.9
     ```

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/youtube-trailers-downloader.git
   cd youtube-trailers-downloader
   ```

3. **Set Up Virtual Environment**:
   - Create and activate a virtual environment:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

4. **Install Dependencies**:
   - Install required libraries:
     ```bash
     pip install -r requirements.txt
     ```

---

## Configuration

The project uses a `config.yaml` file for settings. A template is provided as `config.example.yaml`. To configure the project:

1. Copy the template file:
   ```bash
   cp config.example.yaml config.yaml
   ```

2. Edit the `config.yaml` file to customize the settings.

### Configuration Parameters

```yaml
channels:
  - https://www.youtube.com/c/movieclipstrailers
  - https://www.youtube.com/user/trailers
max_videos_per_channel: 5
max_video_age_months: 3
delete_videos_older_than_months: 6
max_storage_gb: 5
max_resolution: 1080
output_folder: "./trailers"
flatten_output_folder: true
```

- **channels**: List of YouTube channels to monitor for trailers.
- **max_videos_per_channel**: Limit the number of videos downloaded per channel.
- **max_video_age_months**: Only download videos uploaded within the last X months.
- **delete_videos_older_than_months**: Delete videos older than this age.
- **max_storage_gb**: Maximum total storage size for downloaded videos.
- **max_resolution**: Maximum video resolution (e.g., 480, 1080).
- **output_folder**: Path to the folder for storing trailers.

---

## Running the Script

1. **Run the Script**:
   ```bash
   python main.py
   ```

2. **Prevent Simultaneous Execution**:
   - The script includes a locking mechanism to prevent multiple instances from running simultaneously. If a second instance is launched while the first is running, it will exit gracefully with a log message.

---

## Automating with Cron

To schedule the script to run automatically, use `cron`:

1. Open the crontab editor:
   ```bash
   crontab -e
   ```

2. Add the following entry to schedule the script (e.g., every day at 2 AM):
   ```bash
   0 2 * * * /path/to/venv/bin/python /path/to/youtube-trailers-downloader/main.py
   ```

3. Save and exit the crontab editor. The script will now run automatically based on the schedule.

---

## Legal Disclaimer

This project is intended solely for **educational, research, and personal use**. It is not intended for commercial purposes or public redistribution. By using this project, you agree to the following:

1. **Respect YouTube's Terms of Service**: Downloading videos from YouTube may violate their Terms of Service. Ensure you have permission or are otherwise compliant before downloading any content.
2. **No Commercial Use**: This project is not intended for any form of commercial exploitation.
3. **No Warranty**: The software is provided "as is" without warranty of any kind. Use at your own risk.

---

## Notes

- Dynamic data such as the last checked timestamp for channels is stored in a `local.state` file, ensuring that `config.yaml` remains static.
- Regularly review your `config.yaml` and `output_folder` to ensure compliance with storage and download preferences.


## Sync Script

The `sync.py` script generates an XML file from video files in the specified trailer folder. It formats the XML with video metadata and ensures compatibility with Jellyfin's media parsing rules.

### How to Run

1. Ensure your `config.yaml` is set up with the correct paths for `output_folder` and `output_xml_file`.
2. Run the script using Python:

   ```bash
   python sync.py
   ```

### What It Does

- Scans the specified trailer folder for video files (`.mp4` and `.webm`).
- Generates an XML file with metadata for each video.
- Formats the XML with proper indentation and includes necessary schema attributes.