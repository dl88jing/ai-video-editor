import gradio as gr
import json
import ast
import os
from video_utils import get_transcript, stitch_video_segments, get_video_metadata, download_youtube_video, get_video_metadata_long_video
from ai_utils import model, user_input, user_input_with_metadata
from translation_utils import dub_video_translate, get_video, get_video2
from config import GEMINI_API_KEY
import google.generativeai as genai

def process_video(video_path, prompt, language, is_new=False):
    video_name = os.path.basename(video_path)
    output_transcript = get_transcript(video_path, language=language)

    print("Output transcript of video: ", output_transcript)

    genai.configure(api_key=GEMINI_API_KEY)

    generation_config = {
        "temperature": 1,
        "top_p": 0,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        safety_settings=safety_settings,
        generation_config=generation_config,
    )

    # Check if chat is None, and if so, start a new chat session
    chat = model.start_chat() if is_new else None
    if chat is None:
        chat = model.start_chat()
    
    transcript_combined = user_input(chat, output_transcript, prompt, video_name, is_new)
    transcript_combined = ast.literal_eval(transcript_combined)
    
    try:
        transcript_combined2 = json.dumps(transcript_combined, indent=4)
    except:
        transcript_combined2 = str(transcript_combined)
        print("Pretty print failed")

    print("Output transcript after edited: ", transcript_combined2)

    
    processed_video = stitch_video_segments(video_path, transcript_combined, 'stitched_vid.mp4')  
    
    return processed_video, video_name, transcript_combined2

def process_video_with_metadata(video_path, prompt, is_new=True):
    video_name = os.path.basename(video_path)

    genai.configure(api_key=GEMINI_API_KEY)

    generation_config = {
        "temperature": 1,
        "top_p": 0,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        safety_settings=safety_settings,
        generation_config=generation_config,
    )

    chat = model.start_chat()

    # check if video_name.jsonl exists in video_metadata directory
    if os.path.exists(f"video_metadata/{video_name}.jsonl"):
        #load it as a text file
        with open(f"video_metadata/{video_name}.jsonl", "r") as file:
            output_metadata = file.read()
        
        print("Existing metadata found for video")
        print("Output metadata of video: ", output_metadata)
    else:
        output_metadata = get_video_metadata(video_path)
        print("Output metadata of video: ", output_metadata)
    

    print("Output metadata of video: ", output_metadata)

    chat = model.start_chat() if is_new else None
    
    transcript_combined = user_input_with_metadata(chat, output_metadata, prompt, video_name, is_new)
    transcript_combined = ast.literal_eval(transcript_combined)
    
    try:
        transcript_combined2 = json.dumps(transcript_combined, indent=4)
    except:
        transcript_combined2 = str(transcript_combined)
        print("Pretty print failed")

    print("Output transcript after edited: ", transcript_combined2)

    
    processed_video = stitch_video_segments(video_path, transcript_combined, 'stitched_vid.mp4')  
    
    return processed_video, video_name, transcript_combined2



with gr.Blocks() as demo:
    gr.Markdown("# AI Video Remixer")
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
    #     model_name="gemini-1.5-pro",
    #     safety_settings=safety_settings,
    #     generation_config=generation_config,
    # )
    

    # chat = model.start_chat()

    with gr.Row():
        with gr.Column():
            youtube_url_input = gr.Textbox(label="YouTube URL")
            download_youtube_button = gr.Button("Download YouTube Video")
        with gr.Column():
            downloaded_video_output = gr.Video(label="Downloaded Video")

    
    with gr.Row():
        with gr.Column():
            video_input = gr.Video(label="Upload Video")
        
        with gr.Column():
            video_output = gr.Video(label="Processed Video")
            
    with gr.Row():
        prompt_input = gr.Textbox(label="Prompt-to-edit")
        language_input = gr.Dropdown(
                        choices=["en", "es", "hi", "fr", "de", "it", "pt", "nl", "ru", "zh", "ja", "ko"],
                        label="Target Language",
                        value="en"  # Set a default value
                    )
    with gr.Row():
        with gr.Column():
            get_video_metadata_btn = gr.Button("Get Video Metadata")
            #get_video_metadata_long_video_btn = gr.Button("Get Video Metadata Long Video")
            get_transcript_button = gr.Button("Get Transcript")
        with gr.Column():
            process_button2 = gr.Button("Process New Video")
            process_button = gr.Button("Continue Editing Video")
            process_button3 = gr.Button("Process Video with Metadata")

    with gr.Row():
        video_name_output = gr.Textbox(label="Video Name")
    with gr.Row():
        transcript_output = gr.Textbox(label="Processed Output")
    with gr.Row():
        video_description_output = gr.Textbox(label="Video Metadata")

    with gr.Row():
        dub_video_btn = gr.Button("Dub video without lip sync")
        dub_video_btn2 = gr.Button("Dub video with lip sync")
        target_language = gr.Dropdown(
                            choices=["English", "Spanish", "Hindi", "French", "German", "Italian", "Portuguese", "Dutch", "Russian", "Chinese",  "Japanese", "Korean"],
                            label="Target Language",
                            value="English"  # Set a default value
                        )
    with gr.Row():
        with gr.Column():
            translated_video_out = gr.Video(label="Translated Video")
        with gr.Column():
            translated_video_out2 = gr.Video(label="Translated Video2")
       

    dub_video_btn.click(get_video, inputs=[target_language], outputs=[translated_video_out])
    dub_video_btn2.click(get_video2, inputs=[target_language], outputs=[translated_video_out2])
    get_video_metadata_btn.click(get_video_metadata, inputs=[video_input], outputs=[video_description_output])
    #get_video_metadata_long_video_btn.click(get_video_metadata_long_video, inputs=[video_input], outputs=[video_description_output])
    get_transcript_button.click(get_transcript, inputs=[video_input, language_input], outputs=[transcript_output])
    process_button.click(process_video, inputs=[video_input, prompt_input, language_input], outputs=[video_output, video_name_output, transcript_output])
    process_button2.click(lambda *args: process_video(*args, is_new=True), inputs=[video_input, prompt_input, language_input], outputs=[video_output, video_name_output, transcript_output])
    process_button3.click(process_video_with_metadata, inputs=[video_input, prompt_input], outputs=[video_output, video_name_output, video_description_output])
    download_youtube_button.click(download_youtube_video, inputs=[youtube_url_input], outputs=[downloaded_video_output])

if __name__ == "__main__":
    demo.launch()