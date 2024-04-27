from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from openai_whisper import whisper

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'mp4', 'wav', 'ogg', 'm4a'}

# Load the Whisper model
model = whisper.load_model("medium")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the file for transcription
        transcription = transcribe(file_path)

        # Optionally, remove the file after processing if not needed
        os.remove(file_path)

        return jsonify({'transcript': transcription})
    else:
        return jsonify({'error': 'File type not allowed'}), 400

def transcribe(audio_path):
    audio = whisper.load_audio(audio_path)
    result = model.transcribe(audio)
    return result['text']

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
