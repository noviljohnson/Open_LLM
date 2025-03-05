# import streamlit as st
# import cv2
# import numpy as np
# import time
# from subtitle_utils import load_subtitles

# def display_video(video_path):
#     """Display a video from a local file."""
#     # Create a video capture object
#     cap = cv2.VideoCapture(video_path)

#     # Get video properties
#     fps = int(cap.get(cv2.CAP_PROP_FPS))
#     frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#     # Create a Streamlit video component
#     st.write("Video:")
#     video_container = st.empty()

#     while True:
#         # Read a frame from the video
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Convert the frame to a Streamlit-compatible format
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         frame = frame[:, :, ::-1]

#         # Display the frame
#         video_container.image(frame, width=frame_width, height=frame_height)

#         # Wait for the next frame
#         time.sleep(1 / fps)

#     # Release the video capture object
#     cap.release()

# def display_subtitles(subtitles_path):
#     """Display subtitles from a local file."""
#     # Load subtitles
#     subtitles = load_subtitles(subtitles_path)

#     # Create a Streamlit text component for displaying subtitles
#     st.write("Subtitles:")
#     subtitles_container = st.empty()

#     # Initialize a counter for tracking the current subtitle
#     current_subtitle_index = 0

#     while True:
#         # Check if the current subtitle has expired
#         if subtitles[current_subtitle_index].end_time <= time.time():
#             current_subtitle_index += 1
#             if current_subtitle_index >= len(subtitles):
#                 break

#         # Display the current subtitle
#         subtitles_container.text(subtitles[current_subtitle_index].text)

#         # Wait for the next subtitle
#         time.sleep(0.1)

# def load_subtitles(subtitles_path):
#     """Load subtitles from a local file."""
#     # Load subtitles from the file
#     subtitles = []
#     with open(subtitles_path, "r") as f:
#         lines = f.readlines()
#         for i in range(0, len(lines), 4):
#             start_time = float(lines[i + 1].split("-->")[0].strip())
#             end_time = float(lines[i + 1].split("-->")[1].strip())
#             text = lines[i + 2].strip()
#             subtitles.append({"start_time": start_time, "end_time": end_time, "text": text})

#     return subtitles

# def main():
#     st.title("Local Video Player with Subtitles")

#     # Get the video and subtitles file paths
#     video_path = st.text_input("Enter the video file path:")
#     subtitles_path = st.text_input("Enter the subtitles file path:")

#     # Check if both file paths are provided
#     if video_path and subtitles_path:
#         # Display the video and subtitles
#         display_video(video_path)
#         # display_subtitles(subtitles_path)  # Un-comment this line when the video is finished playing

# if __name__ == "__main__":
#     main()


import streamlit as st
import cv2
import numpy as np
import time
import json

def display_video(video_path):
    """Display a video from a local file."""
    # Create a video capture object
    cap = cv2.VideoCapture(video_path)

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Create a Streamlit video component
    st.write("Video:")
    video_container = st.empty()

    frame_start_time = time.time()

    while True:
        # Read a frame from the video
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to a Streamlit-compatible format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = frame[:, :, ::-1]

        # Display the frame
        video_container.image(frame, use_column_width=True)

        # Wait for the next frame
        frame_duration = 1 / fps
        time.sleep(max(0, frame_duration - (time.time() - frame_start_time)))
        frame_start_time = time.time()

    # Release the video capture object
    cap.release()

def display_subtitles(subtitles, start_time):
    """Display subtitles."""
    # Create a Streamlit text component for displaying subtitles
    st.write("Subtitles:")
    subtitles_container = st.empty()

    current_subtitle_index = 0
    current_time = start_time

    while True:
        if current_subtitle_index >= len(subtitles):
            break

        subtitle = subtitles[current_subtitle_index]
        start_time = subtitle[1]
        end_time = subtitle[2]
        text = subtitle[3]

        if current_time >= start_time:
            subtitles_container.text(text)

        if current_time >= end_time:
            current_subtitle_index += 1

        time.sleep(0.1)
        current_time += 0.1

def load_subtitles(subtitles_path):
    """Load subtitles from a local file."""
    # Load subtitles from the file
    with open(subtitles_path, "r") as f:
        subtitles = json.load(f)

    return subtitles

def main():
    st.title("Local Video Player with Subtitles")


    # Get the video and subtitles file paths
    video_path = st.text_input("Enter the video file path:") #r"N:\Open_LLM\spch_dirz\data\playlist [playlist].mp4"
    subtitles_path = st.text_input("Enter the subtitles file path:") #r"N:\Open_LLM\spch_dirz\senet_fin_transcript.json"

    # Check if both file paths are provided
    if video_path and subtitles_path:
        # Load subtitles
        subtitles = load_subtitles(subtitles_path)

        # Display the video and subtitles
        import threading
        video_thread = threading.Thread(target=display_video, args=(video_path,))
        video_thread.start()

        time.sleep(0.1)  # Wait for the video to start
        subtitles_thread = threading.Thread(target=display_subtitles, args=(subtitles, time.time()))
        subtitles_thread.start()

if __name__ == "__main__":
    main()

# def main():
#     st.title("Local Video Player with Subtitles")

#     # Get the video and subtitles file paths
#     video_path = r"N:\Open_LLM\spch_dirz\data\playlist [playlist].mp4"#st.text_input("Enter the video file path:")
#     subtitles_path = r"N:\Open_LLM\spch_dirz\senet_fin_transcript.json"#st.text_input("Enter the subtitles file path:")

#     # Check if both file paths are provided
#     if video_path and subtitles_path:
#         # Load subtitles
#         subtitles = load_subtitles(subtitles_path)

#         # Display the video and subtitles
#         import threading
#         video_thread = threading.Thread(target=display_video, args=(video_path,))
#         video_thread.start()

#         time.sleep(0.1)  # Wait for the video to start
#         subtitles_thread = threading.Thread(target=display_subtitles, args=(subtitles, time.time()))
#         subtitles_thread.start()

# if __name__ == "__main__":
#     main()