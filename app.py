from flask import Flask, request, render_template, jsonify
from google.cloud import speech
import moviepy.editor as mp
from google.oauth2 import service_account
import json
from io import BytesIO

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Check if a file is part of the posted data
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        try:
            # Extract audio from video file or use direct audio file
            if file.filename.endswith('.mp4'):
                video = mp.VideoFileClip(file)
                audio = video.audio
                audio_buffer = BytesIO()
                audio.write_audiofile(audio_buffer, codec='pcm_s16le', nbytes=2, fps=16000)
                audio_content = audio_buffer.getvalue()
            else:  # Assume the file is an audio file
                audio_content = file.read()

            # Initialize the Google Speech client
            client = speech.SpeechClient()
            audio = speech.RecognitionAudio(content=audio_content)
            config = speech.RecognitionConfig(
                language_code='en-US',
                sample_rate_hertz=16000,
                enable_automatic_punctuation=True
            )

            # Transcribing the audio
            response = client.recognize(config=config, audio=audio)
            transcripts = [result.alternatives[0].transcript for result in response.results]
            return jsonify({"transcripts": transcripts})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
 
