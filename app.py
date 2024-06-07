import os
from flask import Flask, request, jsonify, render_template, send_file
import subprocess
from google.cloud import speech
from google.oauth2 import service_account
import json
import io

app = Flask(__name__)

# Increase the maximum request payload size
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

# Load credentials
key_path = '/etc/secrets/google-credentials.json'
with open(key_path) as key_file:
    credentials_dict = json.load(key_file)
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

# Speech client
client = speech.SpeechClient(credentials=credentials)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['file']
        selected_language = request.form.get('language')
        include_timestamps = request.form.get('timestamps') == 'true'

        if not file or file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        if not selected_language:
            return jsonify({"error": "No language selected"}), 400

        try:
            # Save the file temporarily
            filepath = os.path.join('/tmp', file.filename)
            file.save(filepath)

            # Convert the audio to LINEAR16 using ffmpeg
            output_path = os.path.join('/tmp', 'output.wav')
            command = ['ffmpeg', '-i', filepath, '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', output_path]
            subprocess.run(command, check=True)

            # Read the converted audio
            with open(output_path, 'rb') as audio_file:
                audio_content = audio_file.read()

            # Configure the recognition request with the selected language
            config = speech.RecognitionConfig(
                encoding='LINEAR16',
                sample_rate_hertz=16000,
                language_code=selected_language,
                enable_automatic_punctuation=True,
                enable_word_time_offsets=include_timestamps  # Enable word-level time offsets if requested
            )

            # Recognize the speech
            audio = speech.RecognitionAudio(content=audio_content)
            response = client.recognize(config=config, audio=audio)
            transcripts = []
            for result in response.results:
                for alternative in result.alternatives:
                    if include_timestamps:
                        words_info = [{
                            'word': word_info.word,
                            'start_time': word_info.start_time.total_seconds(),
                            'end_time': word_info.end_time.total_seconds()
                        } for word_info in alternative.words]
                        transcript_text = alternative.transcript
                        for word in words_info:
                            transcript_text += f"\n{word['word']} ({word['start_time']} - {word['end_time']})"
                    else:
                        transcript_text = alternative.transcript

                    transcripts.append(transcript_text)

            # Write transcripts to a text file
            text_file_path = os.path.join('/tmp', 'transcription.txt')
            with open(text_file_path, 'w') as text_file:
                text_file.write("\n\n".join(transcripts))

            return send_file(text_file_path, as_attachment=True, download_name='transcription.txt')

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            # Clean up temporary files
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists(output_path):
                os.remove(output_path)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
