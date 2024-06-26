import os
import json
from moviepy.editor import VideoFileClip, concatenate_videoclips
from pytube import YouTube
from config import GEMINI_API_KEY, ELEVEN_LABS_API_KEY, OPENAI_API_KEY, GROQ_API_KEY
from groq import Groq
import time
from requests.exceptions import RequestException
from openai import OpenAI
import google.generativeai as genai
from vertexai.generative_models import Part, GenerativeModel
import vertexai
import cv2
from PIL import Image
import io
import numpy as np
import gradio as gr

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

                # transcription_to_return is a list
                # return transcription_to_return with new lines when new object and indent 4 spaces
                transcription_to_return2 = json.dumps(transcription_to_return, indent=4)
                return transcription_to_return2
     
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

def get_video_metadata(video_path):
    try:

        # genai.configure(api_key=GEMINI_API_KEY)

        # generation_config = {
        #     "temperature": 1,
        #     "top_p": 0,
        #     "top_k": 64,
        #     "max_output_tokens": 8192,
        #     "response_mime_type": "application/json",
        # }

        # safety_settings = [
        #     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        #     {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        #     {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        #     {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        # ]

        # model = genai.GenerativeModel(
        #     model_name="gemini-1.5-flash",
        #     safety_settings=safety_settings,
        #     generation_config=generation_config,
        # )
        vertexai.init(project='gen-lang-client-0004068608', location="us-west1")
        video_name = os.path.basename(video_path)
        print("video_name", video_name)

        model = GenerativeModel(model_name="gemini-1.5-flash")

        json_format = '''
        [{
          "time_start": "00:00",
          "time_end": "01:00",
          "description": "video_description",
          "objects_in_scene": ["object1", "object2", "object3", ...],
          "dialog": "transcript_of_dialog",
          "characters_in_scene": ["character1", "character2", ...]
        },
        ...
        {
          "time_start": "00:00",
          "time_end": "01:00",
          "description": "video_description",
          "objects_in_scene": ["object1", "object2", "object3", ...],
          "dialog": "transcript_of_dialog",
          "characters_in_scene": ["character1", "character2", ...]
        }]
        '''

        # Prepare the prompt
        prompt = f'''
        Provide a description of the video.
        The description should also contain anything important which people say in the video.
        Include key elements such as:
        
        Main subject or focus
        Setting or environment
        Actions or events occurring
        Notable visual elements or patterns
        Any text or recognizable logos
        Important dialogues or spoken content
        Summarize your observations in 3-4 sentences.

        Make a new json object everytime you identified a change of scene.
        Be as granular as you can.
        If there is anything interesting, make a new json object.
        
        Please provide your video description using this format.
        {json_format}
        mime_type=application/json
        Do not provide any explanation.
        Only output list of JSON.
        '''

        # Read the video file
        with open(video_path, "rb") as file:
            video_content = file.read()

        # Create video part
        video_file = Part.from_data(data=video_content, mime_type="video/mp4")

        # video_file_uri = video_path
        # video_file = Part.from_uri(video_file_uri, mime_type="video/mp4")
        
        # Generate content using Gemini
        contents = [video_file, prompt]
        response = model.generate_content(contents)

        print("Video medata generated: ", response.text)

        # save response.text to a file in directory called video_metadata
        # create directory if it doesn't exist
        if not os.path.exists("video_metadata"):
            os.makedirs("video_metadata")

        # save response.text to a file in directory called video_metadata
        # save it as a jsonl file
        with open(f"video_metadata/{video_name}.jsonl", "w") as f:
            f.write(response.text)

        return response.text

    except Exception as e:
        print(f"Error describing video: {e}")
        return "Unable to generate video description."

def get_video_metadata_long_video(video_path):
    try:
        vertexai.init(project='gen-lang-client-0004068608', location="us-west1")
        video_name = os.path.basename(video_path)
        print("video_name", video_name)

        model = GenerativeModel(model_name="gemini-1.5-flash")

        json_format = '''
        [{
          "time_start": "00:00",
          "time_end": "01:00",
          "description": "video_description",
          "objects_in_scene": ["object1", "object2", "object3", ...],
          "dialog": "transcript_of_dialog",
          "characters_in_scene": ["character1", "character2", ...]
        },
        ...
        {
          "time_start": "00:00",
          "time_end": "01:00",
          "description": "video_description",
          "objects_in_scene": ["object1", "object2", "object3", ...],
          "dialog": "transcript_of_dialog",
          "characters_in_scene": ["character1", "character2", ...]
        }]
        '''

        prompt = f'''
        Provide a description of the video.
        The description should also contain anything important which people say in the video.
        Include key elements such as:
        
        Main subject or focus
        Setting or environment
        Actions or events occurring
        Notable visual elements or patterns
        Any text or recognizable logos
        Important dialogues or spoken content
        Summarize your observations in 3-4 sentences.

        Make a new json object everytime you identified a change of scene.
        Be as granular as you can.
        If there is anything interesting, make a new json object.
        
        Please provide your video description using this format.
        {json_format}
        mime_type=application/json
        Do not provide any explanation.
        Only output list of JSON.
        '''

        # Get the length of the video clip
        video = VideoFileClip(video_path)
        video_duration = video.duration
        print(f"Video duration: {video_duration} seconds")

        # Split the video into smaller clips if longer than 3 minutes
        if video_duration > 180:
            clips = [video.subclip(i, min(i + 180, video_duration)) for i in range(0, int(video_duration), 180)]
        else:
            clips = [video]

        # Create a temporary directory to store the video clips
        temp_dir = "temp_video_clips"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Save each clip to a temporary file
        temp_files = []
        for i, clip in enumerate(clips):
            temp_file = os.path.join(temp_dir, f"clip_{i}.mp4")
            clip.write_videofile(temp_file, codec="libx264", temp_audiofile="temp-audio.m4a", remove_temp=True, audio_codec="aac")
            temp_files.append(temp_file)

        # Create an empty list to store the output of generate_content
        output_list = []

        # For each temporary file, run generate_content and append the output to the list
        for temp_file in temp_files:
            with open(temp_file, "rb") as file:
                video_content = file.read()
            clip_file = Part.from_data(data=video_content, mime_type="video/mp4")
            contents = [clip_file, prompt]
            response = model.generate_content(contents)
            output_list.append(response.text)

        # Concatenate the output list and save it as a jsonl file
        output_text = "\n".join(output_list)

        if not os.path.exists("video_metadata"):
            os.makedirs("video_metadata")

        with open(f"video_metadata/{video_name}.jsonl", "w") as f:
            f.write(output_text)

        # Remove the temporary directory and files
        for temp_file in temp_files:
            os.remove(temp_file)
        os.rmdir(temp_dir)

        return output_text

    except Exception as e:
        print(f"Error describing video: {e}")
        return "Unable to generate video description."


import cv2
from PIL import Image
import io
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import google.generativeai as genai
from moviepy.editor import VideoFileClip


def describe_video_by_frames(video_path, frame_interval=5):
    try:
        vertexai.init(project='gen-lang-client-0004068608', location="us-west1")

        model = GenerativeModel(model_name="gemini-1.5-flash")
        # genai.configure(api_key=GEMINI_API_KEY)

        # model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        # Prepare the prompt
        prompt = """
        Provide a description of the video based on the sequence of frames provided.
        The description should also contain anything important which people say in the video.
        Include key elements such as:
        1. Main subject or focus
        2. Setting or environment
        3. Actions or events occurring
        4. Notable visual elements or patterns
        5. Any text or recognizable logos
        6. Important dialogues or spoken content
        Summarize your observations in 3 sentences.

        Output a list of JSON where each JSON object is the description per frame.
        Do not output any explanation. 
        Example JSON format:
        jsonCopy{
          "time_start": "00:00",
          "time_end": "01:30",
          "description": "frame_description",
          "objects_in_scene": ["object1", "object2", "object3", ...],
          "dialog": "transcript_of_dialog",
          "characters_in_scene": ["character1", "character2", ...]
        }
        Please provide your video description using this JSON format.
        mime_type=application/json
        Do not provide any explanation.
        Only output list of JSON
        
        """

        # Extract frames from the video using MoviePy
        video = VideoFileClip(video_path)
        frames = []
        
        for t in range(0, int(video.duration), frame_interval):
            frame = video.get_frame(t)
            
            # Convert the frame to PIL Image
            pil_image = Image.fromarray(frame)
            
            # Save the image to a byte stream
            byte_arr = io.BytesIO()
            pil_image.save(byte_arr, format='JPEG')
            image_bytes = byte_arr.getvalue()
            
            # Create a Part object from the image bytes
            image_part = Part.from_data(data=image_bytes, mime_type="image/jpeg")
            frames.append(image_part)

        video.close()

        # Generate content using Gemini
        contents = frames + [prompt]
        response = model.generate_content(contents)
        return response.text
    except Exception as e:
        print(f"Error describing video: {e}")
        return f"Unable to generate video description. Error: {str(e)}"


import cv2
from PIL import Image
import io
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import google.generativeai as genai
from moviepy.editor import VideoFileClip


def describe_video_by_frames(video_path, frame_interval=5):
    try:
        vertexai.init(project='gen-lang-client-0004068608', location="us-west1")

        model = GenerativeModel(model_name="gemini-1.5-flash")
        # genai.configure(api_key=GEMINI_API_KEY)

        # model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        # Prepare the prompt
        prompt = """
        Provide a description of the video based on the sequence of frames provided.
        The description should also contain anything important which people say in the video.
        Include key elements such as:
        1. Main subject or focus
        2. Setting or environment
        3. Actions or events occurring
        4. Notable visual elements or patterns
        5. Any text or recognizable logos
        6. Important dialogues or spoken content
        Summarize your observations in 3 sentences.

        Output a list of JSON where each JSON object is the description per frame.
        Do not output any explanation. 
        Example JSON format:
        jsonCopy{
          "time_start": "00:00",
          "time_end": "01:30",
          "description": "frame_description",
          "objects_in_scene": ["object1", "object2", "object3", ...],
          "dialog": "transcript_of_dialog",
          "characters_in_scene": ["character1", "character2", ...]
        }
        Please provide your video description using this JSON format.
        mime_type=application/json
        Do not provide any explanation.
        Only output list of JSON
        
        """

        # Extract frames from the video using MoviePy
        video = VideoFileClip(video_path)
        frames = []
        
        for t in range(0, int(video.duration), frame_interval):
            frame = video.get_frame(t)
            
            # Convert the frame to PIL Image
            pil_image = Image.fromarray(frame)
            
            # Save the image to a byte stream
            byte_arr = io.BytesIO()
            pil_image.save(byte_arr, format='JPEG')
            image_bytes = byte_arr.getvalue()
            
            # Create a Part object from the image bytes
            image_part = Part.from_data(data=image_bytes, mime_type="image/jpeg")
            frames.append(image_part)

        video.close()

        # Generate content using Gemini
        contents = frames + [prompt]
        response = model.generate_content(contents)
        return response.text
    except Exception as e:
        print(f"Error describing video: {e}")
        return f"Unable to generate video description. Error: {str(e)}"