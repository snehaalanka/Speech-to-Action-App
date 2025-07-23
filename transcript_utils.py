import os
import requests
from dotenv import load_dotenv
import time

# Load the API key from .env file
load_dotenv()
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
headers = {"authorization": API_KEY}

# Upload audio file to AssemblyAI
def upload_audio(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://api.assemblyai.com/v2/upload',
            headers=headers,
            files={'file': f}
        )
    return response.json()['upload_url']

# Request transcription
def transcribe_audio(audio_url):
    json_data = {"audio_url": audio_url}
    response = requests.post(
        'https://api.assemblyai.com/v2/transcript',
        json=json_data,
        headers=headers
    )
    transcript_id = response.json()['id']
    if not transcript_id:
         return "Failed to create transcript: " + response.text
    attempts=0
    max_attempts=20

    # Polling for result
    while attempts < max_attempts:
        polling_response = requests.get(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
            headers=headers
        )
        result = polling_response.json()
        status = result.get('status')
        if status == 'completed':
            return result.get('text','')
        elif status == 'error':
            return "Error: " + result.get('error', 'Unknown error')
        else:
             print(f"Transcription status: {status}")  # debug status
        attempts += 1
        time.sleep(3)
    return "Transcription timed out."
        

# Run when the script is executed directly
if __name__ == "__main__":
    file_path = "file_path"  # Change this to your file name or path
    print("Uploading audio...")
    audio_url = upload_audio(file_path)
    print("Audio uploaded successfully! URL:", audio_url)

    print("Transcribing audio...")
    transcription = transcribe_audio(audio_url)
    print("\nTranscription result:")
    print(transcription)

