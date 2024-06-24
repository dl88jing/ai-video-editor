import gradio as gr
import json
import ast
import os
from video_utils import get_transcript, stitch_video_segments, describe_video, download_youtube_video
from ai_utils import model, user_input
from translation_utils import dub_video_translate, get_video, get_video2

def process_video(video_path, prompt, language, is_new=False):
    video_name = os.path.basename(video_path)
    output_transcript = get_transcript(video_path, language=language)

    print("Output transcript of video: ", output_transcript)

    chat = model.start_chat() if is_new else None
    
    transcript_combined = user_input(chat, output_transcript, prompt, video_name, is_new)
    transcript_combined = ast.literal_eval(transcript_combined)
    
    try:
        transcript_combined2 = json.dumps(transcript_combined, indent=4)
    except:
        transcript_combined2 = str(transcript_combined)
        print("Pretty print failed")
    
    processed_video = stitch_video_segments(video_path, transcript_combined, 'stitched_vid.mp4')  
    
    return processed_video, video_name, transcript_combined2

def process_youtube_video(youtube_url, prompt, language, is_new=False):
    video_path = download_youtube_video(youtube_url)
    if video_path is None:
        return None, "Download failed", "Failed to download YouTube video"
    
    return process_video(video_path, prompt, language, is_new)

with gr.Blocks() as demo:
    gr.Markdown("# ThirteenLabs Smart AI Editor")
    
    with gr.Row():
        with gr.Column():
            video_input = gr.Video(label="Upload Video")
            youtube_url = gr.Textbox(label="YouTube URL")
            download_youtube_button = gr.Button("Download YouTube Video")
            prompt_input = gr.Textbox(label="Prompt-to-edit")
            language_input = gr.Dropdown(choices=["en", "es", "fr", "de", "it", "ja", "ko", "zh"], label="Language", value="en")
            describe_video_button = gr.Button("Describe Video")
            get_transcript_button = gr.Button("Get Transcript")
            process_button = gr.Button("Process Video")
            process_button2 = gr.Button("Process New Video")
            process_youtube_button = gr.Button("Process YouTube Video")
        
        with gr.Column():
            video_output = gr.Video(label="Processed Video")
            video_name_output = gr.Textbox(label="Video Name")
            transcript_output = gr.Textbox(label="Processed Transcript")
            video_description_output = gr.Textbox(label="Video Description")
    
    with gr.Row():
        dub_video_btn = gr.Button("Dub video")
        dub_video_btn2 = gr.Button("Dub video with lip sync")
        target_language = gr.Textbox(label="Target Language")
        response_out = gr.Textbox(label="Translate Status")
    
    with gr.Row():
        translated_video_out = gr.Video(label="Translated Video")
    
    with gr.Row():
        translated_video_out2 = gr.Video(label="Translated Video2")

    dub_video_btn.click(fn=get_video, inputs=[], outputs=[translated_video_out])
    dub_video_btn2.click(fn=get_video2, inputs=[], outputs=[translated_video_out2])
    describe_video_button.click(fn=describe_video, inputs=[video_input], outputs=[video_description_output])
    get_transcript_button.click(fn=get_transcript, inputs=[video_input, language_input], outputs=[transcript_output])
    process_button.click(fn=process_video, inputs=[video_input, prompt_input, language_input], outputs=[video_output, video_name_output, transcript_output])
    process_button2.click(fn=lambda *args: process_video(*args, is_new=True), inputs=[video_input, prompt_input, language_input], outputs=[video_output, video_name_output, transcript_output])
    process_youtube_button.click(fn=process_youtube_video, inputs=[youtube_url, prompt_input, language_input], outputs=[video_output, video_name_output, transcript_output])

if __name__ == "__main__":
    demo.launch()