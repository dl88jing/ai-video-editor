import os
import json
from moviepy.editor import VideoFileClip
from groq import Groq
from config import GEMINI_API_KEY, ELEVEN_LABS_API_KEY, OPENAI_API_KEY, GROQ_API_KEY
import time
from requests.exceptions import RequestException
from openai import OpenAI

#client = OpenAI(api_key=OPENAI_API_KEY)
client = Groq(api_key=GROQ_API_KEY)

def parse_dict_list(input_list):
    return [{'start': item['start'], 'end': item['end'], 'text': item['text']} for item in input_list]

def get_transcript(video_path, language="en", max_retries=3, retry_delay=5):
    if not video_path:
        print("Error: No video path provided")
        return []

    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return []

    audio_path = None
    try:
        # Extract audio from video
        video = VideoFileClip(video_path)
        audio_path = os.path.splitext(video_path)[0] + ".mp3"
        video.audio.write_audiofile(audio_path, codec='libmp3lame')
        video.close()

        for attempt in range(max_retries):
            try:

                with open(audio_path, "rb") as file:
                    transcription = client.audio.transcriptions.create(
                        file=file,
                        #model="whisper-1",
                        model="whisper-large-v3",
                        response_format="verbose_json",
                        language=language,
                        temperature=0.0,
                    )
                
                print("Transcript secured.")

                # parse the transcription data
                transcription_to_return = parse_dict_list(transcription.segments)
     
                return transcription_to_return
                
            
            except (RequestException, Exception) as e:
                print(f"Error during transcription attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("All transcription attempts failed")
                    return []
            
    except Exception as e:
        print(f"Can't get transcription: {e}")
        return []
    finally:
        # Clean up the temporary audio file
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception as e:
                print(f"Failed to remove temporary audio file: {e}")


def download_youtube_video(url, output_path='videos'):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        output_file = stream.download(output_path)
        print(f"Downloaded: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error downloading YouTube video: {e}")
        return None


def stitch_video_segments(video_file, segments, output_file, resolution=None, bitrate='10000k'):
    # Load the video file
    video = VideoFileClip(video_file)
    original_fps = video.fps
    
    if original_fps is None:
        # Set a default frame rate if original_fps is None
        original_fps = 30
    else:
        original_fps = round(original_fps)
    
    print(f"Original FPS: {original_fps}")
    
    # Create a list to store the video segments
    video_segments = []
    print(f"Number of segments: {len(segments)}")
    
    # Iterate over the segments
    for segment in segments:
        start_time = segment['start_time']
        end_time = segment['end_time']
        # Extract the video segment based on start and end times
        video_segment = video.subclip(start_time, end_time)
        video_segments.append(video_segment)
    
    # Concatenate the video segments
    final_video = concatenate_videoclips(video_segments)
    
    # Set the output video parameters
    output_params = {
        'codec': 'libx264',
        'fps': original_fps,
        'bitrate': bitrate,
        'preset': 'slow',
        'audio_codec': 'aac',
        'audio_bitrate': '192k'
    }
    
    # Resize the video if resolution is specified
    if resolution is not None:
        final_video = final_video.resize(resolution)
    
    # Write the final video to a file
    final_video.write_videofile(output_file, **output_params)
    
    # Close the video clips
    video.close()
    final_video.close()
    
    return output_file

def describe_video(video_path):
    try:
    

        # Initialize Gemini model
        model = GenerativeModel(model_name="gemini-1.5-flash")

        # Prepare the prompt
        prompt = """
        Provide a description of the video.
        The description should also contain anything important which people say in the video.
        Include key elements such as:
        1. Main subject or focus
        2. Setting or environment
        3. Actions or events occurring
        4. Notable visual elements or patterns
        5. Any text or recognizable logos
        6. Important dialogues or spoken content

        Summarize your observations in 3-4 sentences.
        """

        # Read the video file
        with open(video_path, "rb") as file:
            video_content = file.read()

        # Create video part
        video_file = Part.from_data(data=video_content, mime_type="video/mp4")

        # Generate content using Gemini
        contents = [video_file, prompt]
        response = model.generate_content(contents)

        return response.text

    except Exception as e:
        print(f"Error describing video: {e}")
        return "Unable to generate video description."