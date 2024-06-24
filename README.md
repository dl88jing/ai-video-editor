# Smart AI Editor

This is a Gradio application that allows you to edit videos using AI. You can upload a video, provide a prompt, and the application will generate a new video based on the prompt. Additionally, you can download YouTube videos, get video metadata, and get transcripts for videos.

## Features

- Upload a video
- Provide a prompt to edit the video
- Select the language for transcription
- Get video metadata
- Get video transcript
- Process a new video with the provided prompt
- Process a video with metadata
- Download a YouTube video
- Dub the video in a different language
- Dub the video with lip sync in a different language

## Usage

1. Run the `main.py` file to launch the Gradio application.
2. Upload a video or provide a YouTube URL to download a video.
3. Enter a prompt to edit the video.
4. Select the language for transcription (if needed).
5. Click the appropriate button to perform the desired action:
   - "Get Video Metadata" to retrieve metadata for the uploaded video
   - "Get Transcript" to get the transcript of the uploaded video
   - "Process New Video" to process a new video with the provided prompt
   - "Process Video with Metadata" to process a video with metadata
   - "Download YouTube Video" to download a video from YouTube
   - "Dub video" to dub the video in a different language
   - "Dub video with lip sync" to dub the video with lip sync in a different language
6. The processed video, video name, transcript, and other outputs will be displayed in the respective output fields.

## Dependencies

The following dependencies are required to run this application:

- gradio
- moviepy
- pytube
- openai
- google.generativeai
- vertexai
- cv2
- PIL
- numpy

Make sure to install these dependencies before running the application.

## Configuration

You need to provide the following API keys in the `config.py` file:

- `GEMINI_API_KEY`
- `ELEVEN_LABS_API_KEY`
- `OPENAI_API_KEY`
- `GROQ_API_KEY`

Replace the placeholders with your actual API keys.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
