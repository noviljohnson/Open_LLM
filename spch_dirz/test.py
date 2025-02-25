## pyannote/speaker-diarization
from transformers import pipeline
import pyannote

# Load Whisper model for transcription
asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base")


# Load audio file
audio_file = "/mnt/c/Users/Novilsaikumar.A/Downloads/test_audio.wav"
audio_file = "/mnt/c/Users/Novilsaikumar.A/Downloads/meeting_audio_wav.wav"


# Perform transcription
transcription = asr_pipeline(audio_file, return_timestamps=True)


# Load pyannote for speaker diarization (example)
# Note: You need to install pyannote.audio and adjust this part according to your needs
from pyannote.audio import Pipeline
diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token="hf_key")


# Perform speaker diarization
diarization = diarization_pipeline(audio_file)

speaker_talk = ""
# Print speaker segments
for turn, _, speaker in diarization.itertracks(yield_label=True):
    speaker_talk += "\n" + f"Speaker {speaker} speaks from {turn.start:.1f}s to {turn.end:.1f}s, text: {_}"

print(speaker_talk)
# Example: Combine transcript and diarization
transcript_segments = result["segments"]  # Whisper segments with timestamps
for segment in transcript_segments:
    start_time = segment["start"]
    end_time = segment["end"]
    text = segment["text"]

    # Find the corresponding speaker
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        if turn.start <= start_time and turn.end >= end_time:
            print(f"Speaker {speaker}: {text}")
            break
