import os
from flask import Flask, request, jsonify, render_template, send_file
import openai
import json

app = Flask(__name__)

# Increase the maximum request payload size
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25 MB

# Set your OpenAI API key
openai.api_key = 'openai-api-key'

# Directory to store uploaded chunks
UPLOAD_FOLDER = '/tmp/uploads'
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
        combined_file_path = os.path.join(UPLOAD_FOLDER, 'combined_audio.mp3')
        with open(combined_file_path, 'wb') as combined_file:
            for i in range(1, int(request.form['totalChunks']) + 1):
                chunk_filename = os.path.join(UPLOAD_FOLDER, f'chunk_{i}')
                with open(chunk_filename, 'rb') as chunk_file:
                    combined_file.write(chunk_file.read())
                os.remove(chunk_filename)  # Clean up chunk file

        # Use OpenAI Whisper API for transcription
        with open(combined_file_path, 'rb') as audio_file:
            response = openai.Audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"] if include_timestamps
