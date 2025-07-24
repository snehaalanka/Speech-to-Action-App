import requests
import os
from dotenv import load_dotenv
import re
from transformers import pipeline

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

load_dotenv()
API_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def extract_tasks_from_text(transcribed_text):
    summary = summarizer(transcribed_text, max_length=100, min_length=30, do_sample=False)[0]["summary_text"]

    pattern = r"(I (have|got|need|want) to\s.*?)(\.|,|$)"
    matches = re.findall(pattern, transcribed_text, re.IGNORECASE)

    tasks = []
    for match in matches:
        task = match[0]
        task = re.sub(r"^I (have|got|need|want) to\s", '', task, flags=re.IGNORECASE)
        tasks.append("- " + task.strip().capitalize())

    return tasks


