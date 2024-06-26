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

def user_input(chat, transcript, user_input, video_name, chat_new=False,model_input=None):
    if chat is None:
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

    json_format = '''
    [{'transcription': "transcription",
     'start_time': start_time,
     'end_time': end_time},
     ...
     {'transcription': "transcription",
     'start_time': start_time,
     'end_time': end_time}]
    '''
 
    prompt = f'''
    This is a transcription of a video of a sports press conference
    The video title is {video_name}.
    TRANSCRIPT START
    {transcript}
    TRANSCRIPT ENDED
    Output multiple items of transcription that is relevant to the intruction to form a coherent video.
    Make the output chronological in order.
    Make sure the speech throughout the video is smooth and coherent, combine multiple lines of transcript when possible to form a coherent narrative.
    This is the instruction on how to create a highlight video reel by the user:
    {user_input}
    Calculate the first start time and the last end time and stay within the time length duration requested in the instruction by the user.
    Think step by step.  Remember to stay within time length duration of video.
    User this json format {json_format}
    Output in json list format.
    '''
    
    return get_chat_response(chat, prompt)

def user_input_with_metadata(chat, video_metadata, user_input, video_name, chat_new=False,model_input=None):

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

    json_format = '''
    [{'metadata': "metadata",
     'start_time': start_time,
     'end_time': end_time},
     ...
     {'metadata': "metadata",
     'start_time': start_time,
     'end_time': end_time}]
    '''
 
    prompt = f'''
    This is the video name: 
    {video_name}
    This is the metadata of a video that includes time_start, time_end, description, objects_in_scene, dialog, characters_in_scene
    METADATA START
    {video_metadata}
    METADATA END
    Output multiple items of video clips that is relevant to the instruction to form a coherent video.
    Make the output chronological in order.
    Make sure the video is enticing, smooth and coherent, combine multiple lines of video clips when possible to form a coherent narrative.
    This is the instruction on how to create a highlight video reel by the user:
    {user_input}
    Calculate the first start time and the last end time and stay within the time length duration requested in the instruction by the user.
    Think step by step.  Remember to stay within time length duration of video.
    User this json format {json_format}
    Output in json list format.
    '''
    
    return get_chat_response(chat, prompt)