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

 
