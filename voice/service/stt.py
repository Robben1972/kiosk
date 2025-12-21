import requests
from environs import Env
import os

env = Env()
env.read_env()

api_key = env.str("MUXLISA_AI")

def stt(file_path):
    url = 'https://uzbekvoice.ai/api/v1/stt'
    headers = {
        "Authorization": api_key
    }

    file_to_send = file_path

    files = {"file": ("audio.mp3", file_to_send)}

    data = {
        "return_offsets": "true",
        "run_diarization": "false",
        "language": "uz",
        "blocking": "true",
    }

    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Request failed with status code {response.status_code}: {response.text}"
    except requests.exceptions.Timeout:
        return "Request timed out. The API response took too long to arrive."
    
