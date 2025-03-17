import os
import yt_dlp
import boto3
import concurrent.futures
import json
from tqdm import tqdm

# AWS S3 Configuration
AWS_ACCESS_KEY = "your-access-key"
AWS_SECRET_KEY = "your-secret-key"
S3_BUCKET_NAME = "your-bucket-name"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Directory for temporary downloads
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Logs for downloaded and failed videos
DOWNLOADED_LOG = "downloaded_videos.json"
FAILED_LOG = "failed_videos.json"

# Sample list of videos
videos = [
    {
        "m3u8_link": "https://sg002-li.net/...playlist.m3u8",
        "description": "Test Meeting",
        "location": "House Chamber",
        "actual": {"date": "2025-03-15"}
    },
    # Add more video dictionaries here
]

# Function to save logs
def save_log(file_name, data):
    try:
        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        existing_data.append(data)
        with open(file_name, "w") as f:
            json.dump(existing_data, f, indent=4)
    except Exception as e:
        print(f"Error writing to log {file_name}: {e}")

# Function to upload file to S3
def s3_upload(file_path, file_name):
    try:
        folder_name = os.path.splitext(file_name)[0]  # Remove .mp4 extension
        s3_key = f"{folder_name}/{file_name}"  # Create folder and place file inside

        print(f"Uploading {file_name} to S3 in folder '{folder_name}'...")
        s3_client.upload_file(file_path, S3_BUCKET_NAME, s3_key)
        print(f"Uploaded {file_name} successfully to {folder_name}/")

    except Exception as e:
        print(f"Error uploading {file_name}: {e}")
        save_log(FAILED_LOG, {"video": file_name, "error": str(e)})

# Function to download video
def download_video(video):
    filename = f"{video['description']}_{video['location']}_{video['actual']['date']}.mp4"
    filename = filename.replace(" ", "_")  # Ensure no spaces in filename
    output_path = os.path.join(DOWNLOAD_DIR, filename)

    ydl_opts = {
        "format": "best",
        "outtmpl": output_path,
        "quiet": True,
    }

    try:
        print(f"Downloading: {filename}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video["m3u8_link"]])

        # Upload to S3
        s3_upload(output_path, filename)

        # Log successful download
        save_log(DOWNLOADED_LOG, video)

    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        save_log(FAILED_LOG, {"video": video, "error": str(e)})

    finally:
        # Delete file after upload
        if os.path.exists(output_path):
            os.remove(output_path)
            print(f"Deleted {output_path} after upload.")

# Run parallel downloads with tqdm progress bar
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    future_to_video = {executor.submit(download_video, video): video for video in videos}
    
    with tqdm(total=len(videos), desc="Downloading & Uploading Videos", unit="video") as pbar:
        for future in concurrent.futures.as_completed(future_to_video):
            future.result()  # Ensures any raised exceptions are caught
            pbar.update(1)  # Update progress bar

print("All downloads, uploads, and cleanup completed!")
