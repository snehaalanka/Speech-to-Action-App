from transcript_utils import get_transcription
from nlp_task_parser import extract_tasks_from_text

if __name__ == "__main__":
    file_path = "WhatsApp Ptt 2025-07-24 at 12.15.34 PM.mp3"

    # Transcribe the audio file
    transcribed_text = get_transcription(file_path)
    print("\n--- Transcription ---")
    print(transcribed_text)

    #  Extract tasks / to-do list from the transcribed text
    print("\n--- To-Do List ---")
    for task in extract_tasks_from_text(transcribed_text):
      print(task)

