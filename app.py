import os
import json
from flask import Flask, request, render_template, jsonify
from google.cloud import speech
from google.oauth2 import service_account
import moviepy.editor as mp
from io import BytesIO

app = Flask(__name__)

# Load credentials from the file path where Render mounts Secret Files
key_path = '/etc/secrets/google-credentials.json'
with open(key_path) as key_file:
    credentials_dict = json.load(key_file)
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

# Use the credentials to create a client
client = speech.SpeechClient(credentials=credentials)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        try:
            if file.filename.endswith('.mp4'):
                video = mp.VideoFileClip(file)
                audio = video.audio
                audio_buffer = BytesIO()
                audio.write_audiofile(audio_buffer, codec='pcm_s16le', nbytes=2, fps=16000)
                audio_buffer.seek(0)
                audio_content = audio_buffer.getvalue()
            else:
                audio_content = file.read()

            audio = speech.RecognitionAudio(content=audio_content)
            config = speech.RecognitionConfig(
                language_code='en-US',
                sample_rate_hertz=16000,
                enable_automatic_punctuation=True
            )

            response = client.recognize(config=config, audio=audio)
            transcripts = [result.alternatives[0].transcript for result in response.results]
            return jsonify({"transcripts": transcripts})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
