# YouTube Trailers Downloader

This project is a Python-based script designed to download the latest movie trailers from specified YouTube channels. It organizes, filters, and manages the trailers based on user-defined settings.

---

## Features

- Downloads new trailers from specified YouTube channels.
- Filters downloads by video age and limits the number of videos per channel.
- Deletes old videos to maintain storage limits.
- Ensures downloads are in the max specified resolution (e.g., 480p, 1080p).
- Prevents multiple script instances from running simultaneously to avoid conflicts.

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

