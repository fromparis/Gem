import os
from flask import Flask, request, jsonify, render_template, send_file
import openai
import json

app = Flask(__name__)

# Increase the maximum request payload size
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25 MB

# Retrieve the OpenAI API key from the environment
openai.api_key = os.getenv('OPENAI_API_KEY')

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
                timestamp_granularities=["word"] if include_timestamps else []
            )

        # Extract transcript text and timestamps
        transcripts = []
        if include_timestamps:
            for segment in response['segments']:
                for word_info in segment['words']:
                    transcript_text = f"{word_info['word']} ({word_info['start']} - {word_info['end']})"
                    transcripts.append(transcript_text)
        else:
            transcripts.append(response['text'])

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

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
