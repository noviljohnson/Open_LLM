from transformers import pipeline
import pyannote
import whisper

# Load the Whisper model
model = whisper.load_model("base")

# Load Whisper model for transcription
asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base")


# Load audio file
audio_file = "/mnt/c/Users/Novilsaikumar.A/Downloads/test_audio.wav"
audio_file = "/mnt/c/Users/Novilsaikumar.A/Downloads/meeting_audio_wav.wav"
audio_file = "/mnt/e/Local_deploy_HFM/senate_finance.wav"

# Transcribe the audio file
# audio_path = "/mnt/c/Users/Novilsaikumar.A/Downloads/meeting_audio_2.mp3"

wishper_transcript = model.transcribe(audio_file)
# Perform transcription
# transcription = asr_pipeline(audio_file, return_timestamps=True)


# Load pyannote for speaker diarization (example)
# Note: You need to install pyannote.audio and adjust this part according to your needs
from pyannote.audio import Pipeline
diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token="HF_key")


# Perform speaker diarization
diarization = diarization_pipeline(audio_file, min_speakers=2, max_speakers=5)

speaker_talk = ""
# Print speaker segments
for turn, _, speaker in diarization.itertracks(yield_label=True):
    speaker_talk += "\n" + f"Speaker {speaker} speaks from {turn.start:.1f}s to {turn.end:.1f}s, text: {_}"

print(speaker_talk)
# round the floating point numbers to 2 precisions 

# Example: Combine transcript and diarization
transcript_segments = wishper_transcript["segments"]  # Whisper segments with timestamps
for segment in transcript_segments:
    start_time = round(segment["start"],  2)
    end_time = round(segment["end"], 2)
    text = segment["text"]
    # print(start_time," : ", end_time, " : ", text)
    # Find the corresponding speaker
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(round(turn.start, 2), ":", round(turn.end, 2), "<=:", speaker, ":", start_time, ":", end_time)
        if round(turn.start, 2) <= start_time and round(turn.end, 2) >= end_time:
            print(f"Speaker {speaker}({turn.start}, {turn.end}): {text}")
            break
transcript_whole = []
for segment in transcript_segments:
    start_time = segment["start"]
    end_time = segment["end"]
    text = segment["text"]
    transcript_whole.append((start_time, end_time, text))
diarization_timestamps = []
# Print speaker segments
for turn, _, speaker in diarization.itertracks(yield_label=True):
    diarization_timestamps.append((speaker, turn.start, turn.end))




def combine_transcript_and_diarization(transcript, diarization):
    """
    Combine transcript and diarization results into a unified structure.
    
    Args:
        transcript (list): List of transcript segments in the format [(start, end, text), ...].
        diarization (list): List of diarization segments in the format [(speaker, start, end), ...].
    
    Returns:
        list: Combined results in the format [(speaker, start, end, text), ...].
    """
    combined_results = []

    for t_start, t_end, t_text in transcript:
        best_match = None
        max_overlap = 0

        for speaker, d_start, d_end in diarization:
            # Calculate overlap between transcript segment and diarization segment
            overlap_start = max(t_start, d_start)
            overlap_end = min(t_end, d_end)
            overlap = max(0, overlap_end - overlap_start)

            # Find the best match based on maximum overlap
            if overlap > max_overlap:
                max_overlap = overlap
                best_match = (speaker, d_start, d_end)

        if best_match:
            speaker, d_start, d_end = best_match
            combined_results.append((speaker, t_start, t_end, t_text))

    # Combine consecutive lines for the same speaker    
    merged_results = []
    current_speaker = None
    current_start = None
    current_end = None
    current_text = []

    for speaker, start, end, text in combined_results:
        if speaker == current_speaker:
            # Same speaker, extend the current segment
            current_end = end
            current_text.append(text)
        else:
            # New speaker, save the previous segment
            if current_speaker is not None:
                merged_results.append((current_speaker, current_start, current_end, " ".join(current_text)))
            # Start a new segment
            current_speaker = speaker
            current_start = start
            current_end = end
            current_text = [text]

    # Add the last segment
    if current_speaker is not None:
        merged_results.append((current_speaker, current_start, current_end, " ".join(current_text)))

    return merged_results
  
combined_result = combine_transcript_and_diarization(transcript_whole, diarization_timestamps)
print(combined_result)
import json


with open(f"/mnt/e/Local_deploy_HFM/final_results.json", "w") as f:
    json.dump(combined_result, f, indent=4)
