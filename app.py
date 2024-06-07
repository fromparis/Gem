import os
from flask import Flask, request, jsonify, render_template, send_file
import subprocess
from google.cloud import speech, storage
from google.oauth2 import service_account
import json

app = Flask(__name__)

# Increase the maximum request payload size
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

# Load credentials
key_path = '/etc/secrets/google-credentials.json'
with open(key_path) as key_file:
    credentials_dict = json.load(key_file)
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

# Speech client
speech_client = speech.SpeechClient(credentials=credentials)
# Storage client
storage_client = storage.Client(credentials=credentials)

# Google Cloud Storage bucket name
bucket_name = 'your-bucket-name'

# Directory to store uploaded chunks
UPLOAD_FOLDER = '/persistent/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload_chunk', methods=['POST'])
def upload_chunk():
    file = request.files['file']
    chunk_number = request.form['chunkNumber']
    total_chunks = request.form['totalChunks']

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    chunk_filename = os.path.join(UPLOAD_FOLDER, f'chunk_{chunk_number}')
    file.save(chunk_filename)

    return jsonify({"message": "Chunk uploaded successfully"}), 200

@app.route('/process_file', methods=['POST'])
def process_file():
    selected_language = request.form.get('language')
    include_timestamps = request.form.get('timestamps') == 'true'

    try:
        # Combine chunks into a single file
        combined_file_path = os.path.join(UPLOAD_FOLDER, 'combined_audio.wav')
        with open(combined_file_path, 'wb') as combined_file:
            for i in range(1, int(request.form['totalChunks']) + 1):
                chunk_filename = os.path.join(UPLOAD_FOLDER, f'chunk_{i}')
                with open(chunk_filename, 'rb') as chunk_file:
                    combined_file.write(chunk_file.read())
                os.remove(chunk_filename)  # Clean up chunk file

        # Convert the audio to LINEAR16 using ffmpeg
        output_path = os.path.join(UPLOAD_FOLDER, 'output.wav')
        command = ['ffmpeg', '-i', combined_file_path, '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', output_path]
        subprocess.run(command, check=True)

        # Upload the audio file to Google Cloud Storage
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(os.path.basename(output_path))
        blob.upload_from_filename(output_path)

        # Use LongRunningRecognize with the URI of the uploaded file
        audio = speech.RecognitionAudio(uri=f'gs://{bucket_name}/{os.path.basename(output_path)}')
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=selected_language,
            enable_automatic_punctuation=True,
            enable_word_time_offsets=include_timestamps  # Enable word-level time offsets if requested
        )

        operation = speech_client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=600)

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
        text_file_path = os.path.join(UPLOAD_FOLDER, 'transcription.txt')
        with open(text_file_path, 'w') as text_file:
            text_file.write("\n\n".join(transcripts))

        return send_file(text_file_path, as_attachment=True, download_name='transcription.txt')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up temporary files
        if os.path.exists(combined_file_path):
            os.remove(combined_file_path)
        if os.path.exists(output_path):
            os.remove(output_path)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
