import os
import csv
import wave
import av
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
from transcript_utils import get_transcription
from nlp_task_parser import extract_tasks_from_text

st.set_page_config(page_title="Speech to To‑Do", page_icon="📝")
st.title("🎙️ Speech to To‑Do List")

class AudioRecorder(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.frames.append(frame.to_ndarray())
        return frame

CSV_FILE = "todo_history.csv"

def save_tasks_to_file(tasks):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        for task in tasks:
            writer.writerow([task])

def load_tasks_from_file():
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
        try:
            df = pd.read_csv(CSV_FILE, header=None)
            return df[0].dropna().tolist()
        except Exception as e:
            st.warning(f"Couldn't read saved tasks: {e}")
            return []
    return []


def delete_task(task_to_delete):
    tasks = load_tasks_from_file()
    tasks = [t for t in tasks if t != task_to_delete]
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        for t in tasks:
            writer.writerow([t])

st.subheader("🎤 Record your voice")

ctx = webrtc_streamer(
    key="recorder",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=1024,
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    audio_processor_factory=AudioRecorder,
)

if ctx.audio_processor and st.button("🎧 Save & Transcribe"):
    st.info("Saving audio...")
    audio_data = np.concatenate(ctx.audio_processor.frames, axis=1).flatten().astype(np.int16)

    with wave.open("temp_recording.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(48000)
        wf.writeframes(audio_data.tobytes())

    st.audio("temp_recording.wav", format="audio/wav")

    st.info("Transcribing...")
    transcript = get_transcription("temp_recording.wav")
    if not transcript.strip():
      st.warning("No speech detected in the audio.")
    else:
      st.success("✅ Transcript:")
      st.write(transcript)

      st.info("Extracting tasks...")
      tasks = extract_tasks_from_text(transcript)

    if tasks:
        st.success("📝 Your New Tasks:")
        for task in tasks:
            st.markdown(f"• {task}")
        save_tasks_to_file(tasks)
    else:
        st.info("🤔 No tasks were found in the transcription.")



st.markdown("### 📋 Saved To‑Do List:")

saved_tasks = load_tasks_from_file()

if saved_tasks:
    for task in saved_tasks:
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.write(f"• {task}")
        with col2:
            if st.button("❌", key=task):
                delete_task(task)
                st.rerun()
else:
    st.info("No saved to‑dos yet.")
