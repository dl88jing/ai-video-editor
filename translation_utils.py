import requests
from config import ELEVEN_LABS_API_KEY
import time
from time import sleep

def dub_video_translate(video_path, translated_to_language):
    url = "https://api.elevenlabs.io/v1/dubbing"
    
    data = {
        'file': f'{video_path}',
        'source_lang': 'English',
        'target_lang': f'{translated_to_language}',
        'num_speakers': '1',
        'watermark': 'false',
        'name': 'dubbing-test',
    }
    
    headers = {
        'xi-api-key': ELEVEN_LABS_API_KEY,
        'Content-Type': 'multipart/form-data',
    }
    
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("video")


def dub_video_translate(video_path, translated_to_language, HEYGEN_API_KEY):
    url = "https://api.heygen.com/v1/dubbing"

    data = {
        'file': video_path,
        'source_lang': 'en',
        'target_lang': translated_to_language,
        'num_speakers': 1,
        'watermark': False,
        'name': 'dubbing-test',
    }

    headers = {
        'Authorization': f'Bearer {HEYGEN_API_KEY}',
        'Content-Type': 'application/json',
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json().get("video_url")

def get_video(language_input):

    #timer of 2.5 seconds
    time.sleep(2.5)
    # Placeholder function, replace with actual implementation
    return "translated_vid/spanish-jensen.mp4"

def get_video2(language_input):
    time.sleep(2.5)
    # Placeholder function, replace with actual implementation
    return "translated_vid/hindi-jensen.mp4"