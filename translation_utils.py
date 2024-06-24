import requests
from config import ELEVEN_LABS_API_KEY

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

def get_video():
    # Placeholder function, replace with actual implementation
    return "test.mp4"

def get_video2():
    # Placeholder function, replace with actual implementation
    return "hindi-vid.mp4"