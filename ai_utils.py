import google.generativeai as genai
from config import GEMINI_API_KEY

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

def get_chat_response(chat, prompt):
    responses = chat.send_message(prompt, stream=True)
    return "".join(chunk.text for chunk in responses)

def user_input(chat, transcript, user_input, video_title, chat_new=False, is_drew=False):
    if chat_new:
        chat = model.start_chat()
    
    prompt_type = "youtube video by Drew Binsky" if is_drew else "sports press conference"
    
    prompt = f'''
    This is a transcription of a video of a {prompt_type}
    The video title is {video_title}.
    TRANSCRIPT START
    {transcript}
    TRANSCRIPT ENDED
    Output multiple items of transcription that is relevant to the instruction to form a coherent video.
    Make the output chronological in order.
    Make sure the video is enticing, smooth and coherent, combine multiple lines of transcript when possible to form a coherent narrative.
    This is the instruction on how to create a highlight video reel by the user:
    {user_input}
    Calculate the first start time and the last end time and stay within the time length duration requested in the instruction by the user.
    Think step by step. Remember to stay within time length duration of video.
    Use this json format:
    [{{'transcription': "transcription", 'start_time': start_time, 'end_time': end_time}}, ...]
    Output in json list format.
    '''
    
    return get_chat_response(chat, prompt)