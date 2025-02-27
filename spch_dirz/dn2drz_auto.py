import os
import subprocess
from pyannote.audio import Pipeline
from whisper import load_model
import json

# Step 1: Download Videos
def download_videos(base_url):
    """
    Downloads all videos from the given base URL.
    """
    print("Downloading videos...")
    output_dir = "videos"
    os.makedirs(output_dir, exist_ok=True)

    # Use yt-dlp to download videos
    subprocess.run(["yt-dlp", "-o", f"{output_dir}/%(title)s.%(ext)s", base_url])
    print("Videos downloaded successfully.")
    return output_dir


# Step 2: Extract Audio from Videos
def extract_audio(video_dir):
    """
    Extracts audio from all videos in the given directory.
    """
    print("Extracting audio...")
    audio_dir = "audio"
    os.makedirs(audio_dir, exist_ok=True)

    for video_file in os.listdir(video_dir):
        if video_file.endswith((".mp4", ".mkv", ".webm")):
            video_path = os.path.join(video_dir, video_file)
            audio_path = os.path.join(audio_dir, os.path.splitext(video_file)[0] + ".wav")
            subprocess.run(["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path])
    print("Audio extraction completed.")
    return audio_dir


# Step 3: Generate Transcript for Each Audio File
def generate_transcripts(audio_dir):
    """
    Generates transcripts for all audio files using Whisper.
    """
    print("Generating transcripts...")
    transcript_dir = "transcripts"
    os.makedirs(transcript_dir, exist_ok=True)

    model = load_model("base")  # Load Whisper model
    transcripts = {}

    for audio_file in os.listdir(audio_dir):
        if audio_file.endswith(".wav"):
            audio_path = os.path.join(audio_dir, audio_file)
            result = model.transcribe(audio_path)
            transcript_path = os.path.join(transcript_dir, os.path.splitext(audio_file)[0] + ".txt")
            with open(transcript_path, "w") as f:
                f.write(result["text"])
            transcripts[audio_file] = result["text"]
    print("Transcripts generated successfully.")
    return transcripts


# Step 4: Perform Speech Diarization
def perform_diarization(audio_dir):
    """
    Performs speech diarization to identify speakers and their timestamps.
    """
    print("Performing speech diarization...")
    diarization_dir = "diarization"
    os.makedirs(diarization_dir, exist_ok=True)

    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token="YOUR_HF_TOKEN")
    diarizations = {}

    for audio_file in os.listdir(audio_dir):
        if audio_file.endswith(".wav"):
            audio_path = os.path.join(audio_dir, audio_file)
            diarization = pipeline(audio_path)
            diarization_data = []

            for turn, _, speaker in diarization.itertracks(yield_label=True):
                diarization_data.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })

            diarizations[audio_file] = diarization_data

            # Save diarization data to a JSON file
            diarization_path = os.path.join(diarization_dir, os.path.splitext(audio_file)[0] + ".json")
            with open(diarization_path, "w") as f:
                json.dump(diarization_data, f, indent=4)

    print("Speech diarization completed.")
    return diarizations


# Step 5: Combine Timestamps, Speaker Names, and Transcripts
def combine_results(transcripts, diarizations):
    """
    Combines timestamps, speaker names, and transcripts into a single data structure.
    """
    print("Combining results...")
    combined_results = {}

    for audio_file, transcript in transcripts.items():
        diarization_data = diarizations.get(audio_file, [])
        combined_data = []

        for segment in diarization_data:
            start_time = segment["start"]
            end_time = segment["end"]
            speaker = segment["speaker"]

            # Extract corresponding transcript segment (basic approximation)
            combined_data.append({
                "start_time": start_time,
                "end_time": end_time,
                "speaker": speaker,
                "transcript": transcript  # Placeholder; refine this for better alignment
            })

        combined_results[audio_file] = combined_data

    # Save combined results to a JSON file
    with open("combined_results.json", "w") as f:
        json.dump(combined_results, f, indent=4)

    print("Results combined and saved successfully.")


# Main Workflow
if __name__ == "__main__":
    # Base URL of the webpage containing video links
    base_url = "https://sg001-harmony.sliq.net/00293/Harmony/en/View/RecentEnded/20250224/-1"

    # Step 1: Download videos
    video_dir = download_videos(base_url)

    # Step 2: Extract audio
    audio_dir = extract_audio(video_dir)

    # Step 3: Generate transcripts
    transcripts = generate_transcripts(audio_dir)

    # Step 4: Perform speech diarization
    diarizations = perform_diarization(audio_dir)

    # Step 5: Combine results
    combine_results(transcripts, diarizations)
